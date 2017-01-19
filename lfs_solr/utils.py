# -*- coding: utf-8 -*-

# python imports
import json

# django imports
from django.conf import settings

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import CONFIGURABLE_PRODUCT

# requests imports
import requests
from requests.auth import HTTPBasicAuth

SOLR_ENABLED = settings.SOLR_ENABLED
SOLR_ADDRESS = settings.SOLR_ADDRESS
SOLR_USER = settings.SOLR_USER
SOLR_PASSWORD = settings.SOLR_PASSWORD


class SolrConfigurationException(Exception):
    """ Solr disabled """


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
    data = {
        "delete": {
            "query": "id:%s" % product.id
        }
    }

    requests.post(
        SOLR_ADDRESS + "/update?commit=true",
        headers={"content-type": "application/json"},
        data=json.dumps(data),
        auth=HTTPBasicAuth(SOLR_USER, SOLR_PASSWORD)
    )


def index_all_products():
    """Indexes all products.
    """
    products = Product.objects.filter(
        active=True, sub_type__in=(STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT))

    _index_products(products, delete=True)


def _index_products(products, delete=False):
    """Indexes given products.
    """
    if delete:
        data = {
            "delete": {
                "query": "*:*"
            }
        }

        requests.post(
            SOLR_ADDRESS + "/update?commit=true",
            headers={"content-type": "application/json"},
            data=json.dumps(data),
            auth=HTTPBasicAuth(SOLR_USER, SOLR_PASSWORD)
        )

    data = []
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

        data.append({
            "id": product.id,
            "name": product.get_name(),
            "price": price,
            "categories": categories,
            "keywords": product.get_meta_keywords(),
            "manufacturer": manufacturer_name,
            "sku_manufacturer": product.sku_manufacturer,
            "description": product.description,
        })

    requests.post(
        SOLR_ADDRESS + "/update?commit=true",
        headers={"content-type": "application/json"},
        data=json.dumps(data),
        auth=HTTPBasicAuth(SOLR_USER, SOLR_PASSWORD)
    )
