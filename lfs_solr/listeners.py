# django imports
from django.db.models.signals import post_save

# lfs imports
from lfs.catalog.models import Product
from lfs.core.signals import product_changed

# lfs_solr imports
from lfs_solr.utils import index_product

def product_saved_listener(sender, instance, **kwargs):
    """
    """
    index_product(instance)
post_save.connect(product_saved_listener, sender=Product)

