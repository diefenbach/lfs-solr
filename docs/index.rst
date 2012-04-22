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
  If you don't have a SOLR instance yet, you can use provided zc.buildout 
  example configuration file to generate new Solr instance including
  the schema.xml.

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

3. Setup SOLR_ADDRESS to point to your Solr server. It is set to
   http://127.0.0.1:8983/solr/ by default. You can also set SOLR_ENABLED to
   False if you want to disable Solr integration (eg. for development instance).

4. Add lfs_solr's urls to your project's url.py. Make sure that they are before
   LFS' urls::

    urlpatterns = patterns("",
        (r'', include('lfs_solr.urls')),
        (r'', include('lfs.core.urls')),
        ...
    )

5. If you are not using buildout to generate Solr instance, put the provided 
   schema.xml to your Solr conf directory. In any case start Solr.

7. Start your LFS instance

7. Visit following URL to index your products (this must be done only once)::

    http://<your-domain>/index-products

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
