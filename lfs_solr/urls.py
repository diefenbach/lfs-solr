from django.urls import re_path

from . import views
from .utils import SOLR_ENABLED

urlpatterns = [
    re_path(r"^solr-set-filter", views.set_filter, name="solr_set_filter"),
    re_path(r"^solr-reset-filter", views.reset_filter, name="solr_reset_filter"),
    re_path(r"^solr-reset-field", views.reset_field, name="solr_reset_field"),
    re_path(r"^index-products", views.index_products, name="solr_index_products"),
]

if SOLR_ENABLED:
    urlpatterns += [
        re_path(r"^search", views.search, name="solr_search"),
        re_path(r"^livesearch", views.livesearch, name="solr_livesearch"),
    ]
