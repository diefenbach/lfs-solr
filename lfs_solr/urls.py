# django imports
from django.conf.urls.defaults import patterns, url

# just import to activate listeners. Moved from __init__.py
# due to circular imports
import lfs_solr.listeners
lfs_solr.listeners  # pyflakes

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
