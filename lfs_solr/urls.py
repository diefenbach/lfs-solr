from django.conf.urls import url

from . import views
from . utils import SOLR_ENABLED

urlpatterns = [
    url(r'^solr-set-filter', views.set_filter, name="solr_set_filter"),
    url(r'^solr-reset-filter', views.reset_filter, name="solr_reset_filter"),
    url(r'^solr-reset-field', views.reset_field, name="solr_reset_field"),
    url(r'^index-products', views.index_products, name="solr_index_products"),
]

if SOLR_ENABLED:
    urlpatterns += [
        url(r'^search', views.search, name="solr_search"),
        url(r'^livesearch', views.livesearch, name="solr_livesearch"),
    ]
