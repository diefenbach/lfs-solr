# django imports
from django.conf.urls.defaults import patterns, url

from lfs_solr.utils import SOLR_ENABLED

urlpatterns = patterns('lfs_solr.views',
    url(r'^solr-set-filter', "set_filter", name="solr_set_filter"),
    url(r'^solr-reset-filter', "reset_filter", name="solr_reset_filter"),
    url(r'^solr-reset-field', "reset_field", name="solr_reset_field"),
    url(r'^index-products', "index_products", name="solr_index_products"),
)

if SOLR_ENABLED:
    urlpatterns += patterns('lfs_solr.views',
        url(r'^search', "search", name="solr_search"),
        url(r'^livesearch', "livesearch", name="solr_livesearch"),
    )
