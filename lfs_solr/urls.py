# django imports
from django.conf.urls.defaults import *

urlpatterns = patterns('lfs_solr.views',
    url(r'^search', "search", name="solr_search"),
    url(r'^livesearch', "livesearch", name="solr_livesearch"),
    url(r'^set-filter', "set_filter", name="solr_set_filter"),
    url(r'^set-sorting', "set_sorting", name="solr_set_sorting"),
    url(r'^reset-filter', "reset_filter", name="solr_reset_filter"),
    url(r'^reset-field', "reset_field", name="solr_reset_field"),
    url(r'^index-products', "index_products", name="solr_index_products"),
)
