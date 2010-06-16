# coding: utf-8

# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson

# pysolr imports
from pysolr import Solr

# lfs imports
from lfs.catalog.models import Product

# lfs_solr

try:
    SOLR_ADDRESS = settings.SOLR_ADDRESS
except:
    from lfs_solr.settings import SOLR_ADDRESS

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

    request.session["solr_filter"]  = solr_filter
    return HttpResponseRedirect(reverse("solr_search") + "?q=" + q)

def set_sorting(request):
    """Saves the sorting to current session.
    """
    q = request.GET.get("q")
    sorting = request.GET.get("sorting")

    if sorting:
        request.session["solr_sorting"] = sorting
    else:
        try:
            del request.session["solr_sorting"]
        except KeyError:
            pass

    return HttpResponseRedirect(reverse("solr_search") + "?q=" + q)

def livesearch(request, template_name="lfs_solr/livesearch_results.html"):
    """Renders the results for the live search.
    """
    rows = 10
    q = request.GET.get("q", "")

    if q == "":
        result = simplejson.dumps({
            "state" : "failure",
        })
    else:
        conn = Solr(SOLR_ADDRESS)

        params = {
          'rows' : rows,
        }

        results = conn.search(q.lower(), **params)

        # Products
        products = []
        for doc in results.docs:
            product = Product.objects.get(pk=doc["id"])
            products.append(product)

        products = render_to_string(template_name, RequestContext(request, {
            "products" : products,
            "q" : q,
            "total" : results.hits,
        }))

        result = simplejson.dumps({
            "state" : "success",
            "products" : products,
        })

    return HttpResponse(result)

def search(request, template_name="lfs_solr/search.html"):
    """Provides form and result for search via Solr.
    """
    if request.GET.get("reset"):
        try:
           del request.session["solr_filter"]
        except KeyError:
            pass

    rows = 10
    q = request.GET.get("q")

    try:
        start = int(request.GET.get("start", 0))
    except ValueError:
        start = 0

    if q:
        conn = Solr(SOLR_ADDRESS)

        params = {
          'facet': 'on',
          'facet.field': ['categories', 'manufacturer'],
          'facet.mincount' : 1,
          'rows' : rows,
          "start" : start,
        }

        # Sorting
        sorting = request.session.get("solr_sorting")
        if sorting:
            params["sort"] = sorting

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

        # Facets
        categories = []
        temp = results.facets["facet_fields"]["categories"]
        for i in range(1, len(temp), 2):
            name = temp[i-1]
            if name.find(" "):
                url = '"%s"' % name
            else:
                url = name
            categories.append({
                "url" : url,
                "name" : name,
                "amount" : temp[i],
            })

        manufacturers = []
        temp = results.facets["facet_fields"]["manufacturer"]
        for i in range(1, len(temp), 2):
            name = temp[i-1]
            if name:
                if name.find(" "):
                    url = '"%s"' % name
                else:
                    url = name
                manufacturers.append({
                    "url" : url,
                    "name" : name,
                    "amount" : temp[i],
                })

        # Pagination
        if start + rows < results.hits:
            display_next = True
            next_start = start + rows
        else:
            display_next = False
            next_start = None

        if start-rows >= 0:
            display_previous = True
            previous_start = start - rows
        else:
            display_previous = False
            previous_start = None

        return render_to_response(template_name, RequestContext(request, {
            "products" : products,
            "results" : results,
            "categories" : categories,
            "manufacturers" : manufacturers,
            "categories_reset" : "categories" in request.session.get("solr_filter", []),
            "manufacturer_reset" : "manufacturer" in request.session.get("solr_filter", []),
            "total" : results.hits,
            "display_next" : display_next,
            "next_start" : next_start,
            "previous_start" : previous_start,
            "display_next" : display_next,
            "display_previous" : display_previous,
            "q" : q,
            "sorting" : sorting,
        }))
    else:
        return render_to_response(template_name, RequestContext(request, {}))