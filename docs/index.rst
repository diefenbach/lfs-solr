.. LFS Solr documentation master file, created by
   sphinx-quickstart on Sat Jul  3 14:08:01 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================
Welcome to lfs_solr's documentation!
====================================

What is it?
===========

lfs_solr is the integration of `Solr <http://lucene.apache.org/solr/>`_
into `LFS <http://pypi.python.org/pypi/django-lfs/>`_

Prerequisites
=============

To use lfs_solr you need the following prerequisites:

* `Solr <http://lucene.apache.org/solr/>`_.
  Please see http://lucene.apache.org/solr/tutorial.html for more.

* `LFS <http://pypi.python.org/pypi/django-lfs/>`_.
  Please see http://packages.python.org/django-lfs/introduction/installation.html
  for more.

* `pysolr <http://pypi.python.org/pypi/pysolr>`_. You can just easy_install 
  it (this is done automatically if you install lfs_solr via easy_install)::

    $ easy_install pysolr

Installation
============

1. Put lfs_solr to the PYTHONPATH or install it via easy install::

   $ easy_install lfs_solr

2. Add lfs_solr to INSTALLED_APPS within settings.py of your Django project::

    INSTALLED_APPS = (
        "..."
        "lfs_solr",
        "...",
    )

3. Add lfs_solr's urls to your project's url.py. Make sure that they are before
   LFS' urls::

    urlpatterns = patterns("",
        (r'', include('lfs_solr.urls')),
        (r'', include('lfs.core.urls')),
        ...
    )

4. Put the provided schema.xml to your Solr conf directory and start Solr.

5. Start your LFS instance

6. Visit following URL to index your products (this must be done only once)::

    http://<your-domain>/index-products

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
