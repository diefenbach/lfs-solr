# coding: utf-8

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.core.paginator import Paginator, Page

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.settings import SORTING_MAP
from lfs.search import views as lfssearch_views

# lfs_solr imports
from lfs_solr.utils import _get_solr_connection


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

    if request.session.has_key("solr_filter") == False:
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
        result = simplejson.dumps({
            "state": "failure",
        })
    else:
        conn = _get_solr_connection()

        params = {
          'rows': rows,
        }

        results = conn.search(q.lower(), **params)

        # Products
        products = []
        for doc in results.docs:
            product = Product.objects.get(pk=doc["id"])
            products.append(product)

        products = render_to_string(template_name, RequestContext(request, {
            "products": products,
            "q": q,
            "total": results.hits,
        }))

        result = simplejson.dumps({
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
        conn = _get_solr_connection()

        params = {
          'facet': 'on',
          'facet.field': ['categories', 'manufacturer'],
          'facet.mincount': 1,
          'rows': rows,
          "start": (page - 1) * rows,
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

        if request.session.has_key("solr_filter"):
            params["fq"] = []
            for field, value in request.session["solr_filter"].items():
                params["fq"].append("%s:%s" % (field.encode("utf-8"), value.encode("utf-8")))

        results = conn.search(q.lower(), **params)

        # Products
        products = []
        for doc in results.docs:
            try:
                product = Product.objects.get(pk=doc["id"])
            except Product.DoesNotExist:
                pass
            else:
                products.append(product)

        fake_results = SolrResults(products, results.hits, rows)

        # Facets
        categories = []
        temp = results.facets["facet_fields"]["categories"]
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
        temp = results.facets["facet_fields"]["manufacturer"]
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
            "results": results,
            "categories": categories,
            "manufacturers": manufacturers,
            "categories_reset": "categories" in request.session.get("solr_filter", []),
            "manufacturer_reset": "manufacturer" in request.session.get("solr_filter", []),
            "total": results.hits,
            "q": q,
            "sorting": sorting_value,
            'paginator': paginator,
            'page_obj': page_obj,
        }))
    else:
        return render_to_response(template_name, RequestContext(request, {}))