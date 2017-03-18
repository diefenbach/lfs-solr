# coding: utf-8

import json

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.paginator import Paginator, Page

from lfs.catalog.models import Product
from lfs.catalog.settings import SORTING_MAP

import requests
from requests.auth import HTTPBasicAuth

SOLR_ENABLED = settings.SOLR_ENABLED
SOLR_ADDRESS = settings.SOLR_ADDRESS
SOLR_USER = settings.SOLR_USER
SOLR_PASSWORD = settings.SOLR_PASSWORD


class SolrResults(object):
    def __init__(self, objects, total, per_page):
        self._total = total
        self.objects = objects
        self.per_page = per_page

    def __len__(self):
        return self._total

    def __getitem__(self, index):
        # since there is eg. 10 items in the list only,
        # we return particular item as it was on correct position
        return self.objects[index % self.per_page]


@permission_required("manage_shop", login_url="/login/")
def index_products(request):
    """Indexes full all products.
    """
    from lfs_solr.utils import index_all_products
    index_all_products()

    return HttpResponse("Done!")


def reset_field(request):
    """Resets filter for given field.
    """
    q = request.GET.get("q")
    field = request.GET.get("field")
    try:
        solr_filter = request.session["solr_filter"]
        del solr_filter[field]
    except KeyError:
        pass
    else:
        request.session["solr_filter"] = solr_filter

    return HttpResponseRedirect(reverse("solr_search") + "?q=" + q)


def reset_filter(request):
    """Resets all filters.
    """
    q = request.GET.get("q")
    try:
        del request.session["solr_filter"]
    except KeyError:
        pass

    return HttpResponseRedirect(reverse("solr_search") + "?q=" + q)


def set_filter(request):
    """Saves the filter for given field to current session.
    """
    field = request.GET.get("field")
    value = request.GET.get("value")
    q = request.GET.get("q")

    if "solr_filter" in request.session.keys() is False:
        request.session["solr_filter"] = {}

    solr_filter = request.session["solr_filter"]
    solr_filter[field] = value

    request.session["solr_filter"] = solr_filter
    return HttpResponseRedirect(reverse("solr_search") + "?q=" + q)


def livesearch(request, template_name="lfs/search/livesearch_results.html"):
    """Renders the results for the live search.
    """
    # if not SOLR_ENABLED, urls.py does not call this view
    rows = 10
    q = request.GET.get("q", "")

    if q == "":
        result = json.dumps({
            "state": "failure",
        })
    else:
        params = {
            'rows': rows,
            'q': q,
            'wt': "json",
        }

        result = requests.get(
            SOLR_ADDRESS + "/select",
            headers={"content-type": "application/json"},
            auth=HTTPBasicAuth(SOLR_USER, SOLR_PASSWORD),
            params=params,
        )

        content = json.loads(result.content)
        docs = content["response"]["docs"]

        # Products
        products = []
        for doc in docs:
            product = Product.objects.get(pk=doc["id"])
            products.append(product)

        products = render_to_string(template_name, RequestContext(request, {
            "products": products,
            "q": q,
            "total": content["response"]["numFound"],
        }))

        result = json.dumps({
            "state": "success",
            "products": products,
        })

    return HttpResponse(result)


def search(request, template_name="lfs/search/search_results.html"):
    """Provides form and result for search via Solr.
    """
    # if not SOLR_ENABLED, urls.py does not call this view
    if request.GET.get("reset") or request.GET.get("livesearch"):
        try:
            del request.session["solr_filter"]
        except KeyError:
            pass

    rows = 10
    q = request.GET.get("q")

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    if q:
        params = {
            'facet': 'on',
            'facet.field': ['categories', 'manufacturer'],
            'facet.mincount': 1,
            'rows': rows,
            "start": (page - 1) * rows,
            "q": q,
            "wt": "json",
        }

        # Sorting
        sorting = ''
        sorting_value = request.session.get("sorting")
        if sorting_value:
            # check validity of sort param.
            # Since SOLR uses different sorting keys, we must find
            # correct sorting key
            # Example: session contains -price, we need to sort by 'price desc'
            for item in SORTING_MAP:
                if item['default'] == sorting_value:
                    sorting = item.get('ftx')  # returns correct sort key
                    break
            if sorting:
                params["sort"] = sorting
            else:
                del request.session['sorting']

        if "solr_filter" in request.session.keys():
            params["fq"] = []
            for field, value in request.session["solr_filter"].items():
                params["fq"].append("%s:%s" % (field.encode("utf-8"), value.encode("utf-8")))

        result = requests.get(
            SOLR_ADDRESS + "/select",
            headers={"content-type": "application/json"},
            auth=HTTPBasicAuth(SOLR_USER, SOLR_PASSWORD),
            params=params,
        )

        content = json.loads(result.content)
        docs = content["response"]["docs"]

        # Products
        products = []
        for doc in docs:
            try:
                product = Product.objects.get(pk=doc["id"])
            except Product.DoesNotExist:
                pass
            else:
                products.append(product)

        fake_results = SolrResults(products, content["response"]["numFound"], rows)

        # Facets
        categories = []
        temp = content["facet_counts"]["facet_fields"]["categories"]
        for i in range(1, len(temp), 2):
            name = temp[i - 1]
            if name.find(" "):
                url = '"%s"' % name
            else:
                url = name
            categories.append({
                "url": url,
                "name": name,
                "amount": temp[i],
            })

        manufacturers = []
        temp = content["facet_counts"]["facet_fields"]["manufacturer"]
        for i in range(1, len(temp), 2):
            name = temp[i - 1]
            if name:
                if name.find(" "):
                    url = '"%s"' % name
                else:
                    url = name
                manufacturers.append({
                    "url": url,
                    "name": name,
                    "amount": temp[i],
                })

        paginator = Paginator(fake_results, rows)
        page_obj = Page(fake_results, page, paginator)

        return render_to_response(template_name, RequestContext(request, {
            "products": products,
            "results": content,
            "categories": categories,
            "manufacturers": manufacturers,
            "categories_reset": "categories" in request.session.get("solr_filter", []),
            "manufacturer_reset": "manufacturer" in request.session.get("solr_filter", []),
            "total": content["response"]["numFound"],
            "q": q,
            "sorting": sorting_value,
            'paginator': paginator,
            'page_obj': page_obj,
        }))
    else:
        return render_to_response(template_name, RequestContext(request, {}))
