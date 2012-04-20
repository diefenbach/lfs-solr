from django.conf import settings
# pysolr imports
from pysolr import Solr

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import CONFIGURABLE_PRODUCT

try:
    SOLR_ADDRESS = settings.SOLR_ADDRESS
    SOLR_ENABLED = settings.SOLR_ENABLED
except:
    from lfs_solr.settings import SOLR_ADDRESS, SOLR_ENABLED


class SolrConfigurationException(Exception):
    """ Solr disabled """


def _get_solr_connection():
    if not SOLR_ENABLED:
        raise SolrConfigurationException('SOLR is disabled')
    return Solr(SOLR_ADDRESS)


def index_product(product):
    """Indexes passed product.
    """
    if product.is_variant():
        try:
            product = product.parent.get_default_variant()
        except AttributeError:
            return

    if product and product.active:
        _index_products([product])


def delete_product(product):
    """Deletes passed product from index.
    """
    conn = _get_solr_connection()
    conn.delete(id=product.id)


def index_all_products():
    """Indexes all products.
    """
    products = Product.objects.filter(
        active=True, sub_type__in=(STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT))

    _index_products(products, delete=True)


def _index_products(products, delete=False):
    """Indexes given products.
    """
    conn = _get_solr_connection()
    if delete:
        conn.delete(q='*:*')

    temp = []
    for product in products:

        # Just index the default variant of a "Product with Variants"
        if product.is_product_with_variants():
            product = product.get_default_variant()

        if product is None:
            continue

        # Categories
        categories = []
        for category in product.get_categories():
            categories.append(category.name)

        # Manufacturer
        manufacturer = product.manufacturer
        if manufacturer:
            manufacturer_name = manufacturer.name
        else:
            manufacturer_name = ""

        try:
            # lfs 0.6+
            price = product.get_price(request=None)
        except TypeError:  # TypeError - unexpected argument
            # lfs 0.5
            price = product.get_price()

        temp.append({
            "id": product.id,
            "name": product.get_name(),
            "price": price,
            "categories": categories,
            "keywords": product.get_meta_keywords(),
            "manufacturer": manufacturer_name,
            "sku_manufacturer": product.sku_manufacturer,
            "description": product.description,
        })

    conn.add(temp)