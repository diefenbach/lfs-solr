# django imports
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

# lfs imports
from lfs.catalog.models import Product
from lfs.core.signals import product_changed

# lfs_solr imports
from lfs_solr.utils import index_product
from lfs_solr.utils import delete_product

def product_deleted_listener(sender, instance, **kwargs):
    delete_product(instance)
post_delete.connect(product_deleted_listener, sender=Product)

def product_saved_listener(sender, instance, **kwargs):
    if instance.is_active():
        index_product(instance)
    else:
        delete_product(instance)
post_save.connect(product_saved_listener, sender=Product)

