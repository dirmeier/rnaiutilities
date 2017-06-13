**********
rnaiquery
**********

Easily query and sample  from a large set of CellProfiler-based RNAi screen
file-sets into flat ``tsvs``.

Installation
============

Make sure to have ``python 3`` installed. ``rnai-query`` does not support
previous versions. The best way to do that is to download anaconda_
virtual environment_.

I recommend installing the library using:

.. code-block:: bash

   pip install rnaiquery

This also installs ``ipython`` and all required dependencies.

Usage
=====

First start an ``ipython`` session with:

.. code-block:: bash

  ipython

If you have not worked with ``python`` before, this is similar to an `R`-session.
Having the interpreter started, querying is easy:


.. code-block:: python

  # load the query module
  from rnaiquery import Query
  # create a query object
  q = Query(<your db file>)
  # do a query
  res = q.query(library="d", featureclass="cells", gene="star", sample=10)
  # print to tsv
  res.dump("~/Desktop/bla.tsv")

In this example we use a sqlite database called ``<your db file>``. If you do
not provide an argument to the constructor, we assume that there is a Postgres
database running called ``tix`` that listens on port ``5432``.

The query should get all ``cell``-features where gene ``star`` has been
transturbed using ``dharmacon`` libraries. From every well that has been
found ``10`` cells are randomly sampled. You can create the database (file)
yourself or just use mine. Documentation how the DB is created is found under
 ``/rnai_query/dbms``.

The complete list of possible queries is shown below.

.. code-block:: python

  def query(self,
            study=None,
            pathogen=None,
            library=None,
            design=None,
            replicate=None,
            plate=None,
            gene=None,
            sirna=None,
            well=None,
            featureclass=None,
            sample=100)

There are probably still bugs, so patches are welcome.

Author
======

- Simon Dirmeier <simon.dirmeier@bsse.ethz.ch>

.. _anaconda: https://www.continuum.io/downloads
.. _environment: https://conda.io/docs/using/envs.html