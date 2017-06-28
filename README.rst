**************
rnaiutilities
**************

A collection of python modules and command line toole for processing
image-based RNAi screens.

Introduction
============

`rnaiutilies` provide a set of python modules that can be used to process,
convert, query and analyse imaged-based RNAi-screens.

The packages are designed for the following workflow:

* Download raw `mat` files from an openBIS instance or where ever your data lie.
 The `mat` files are supposed to be created by `CellProfiler`, i.e. platewise
  data-sets, where every file describes a single features for single cells.
* Parse the downloaded data using `rnai-parse`: install the package, and
 process as described in the package folder.
 This generates a list of raw `tsvs` files or a bundled `h5` file. Until now
 the parser writes featuresets for `cells`, `perinuclei`, `nuclei`,  `expandednuclei`,  `bacteria` and `invasomes`.
* Finally cells can be queried using `rnai-query`. For that first meta files
 generated from the step above are written into a database. Then the DB can
 be queried against to subset single genes, sirnas, pathogens, etc. efficiently.

Installation
============

Make sure to have ``python 3`` installed. ``rnaiutilities`` does not support
previous versions. The best way to do that is to download anaconda_
virtual environment_.

Download the latest release first and then install using:

.. code-block:: bash

   pip install .

If you get errors, I probably forgot some dependency.

Usage
=====

rnai-parse
----------


TODO

rnai-query
----------

First a database with meta files has to be setup. For that we use either
``postgres`` or ``sqlite``. You can either

* start ``postgres`` with a database called ``tix`` and make it listen to port
5432,
* or provide a filename to the script and we use it as an stand-alone ``sqlite``
database (use a filename with suffix ``.db``).


 TODO

For postgres:

.. code-block:: bash

  rnai-query insert /i/am/a/path/to/data

For sqlite:

.. code-block:: bash

  rnai-query insert --db /i/am/a/file/called/tix.db /i/am/a/path/to/data


Having the database set up, we can query for custom features.

.. code-block:: bash

  rnai-query query ....


Alternatively you can just use the python API, for example with ``ipython``.
If you have not worked with ``python`` before, this is similar to an
``R``-session. Having the interpreter started (using ``ipython`` on the
command line), querying is easy:


.. code-block:: python

  # load the query module
  from rnaiutilities import Query
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

If any argument is not set, i.e. set to ``None``, all the database will be
searched and no filters applied.

There are probably still bugs, so patches are welcome.

Author
======

- Simon Dirmeier <simon.dirmeier@bsse.ethz.ch>

.. _anaconda: https://www.continuum.io/downloads
.. _environment: https://conda.io/docs/using/envs.html
