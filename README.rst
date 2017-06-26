<h1 align="center"> rnai-utilities </h1>

A collection of python packages for processing image-based RNAi screens.

## Introduction

`rnai-utilies` provide a set of python packages that can be used to process, convert, query and analyse
imaged-based RNAi-screens.

## Usage

The packages are designed for the following workflow:

* Download raw `mat` files from an openBIS instance or whereever your data lie. The `mat` files are supposed to be created by `CellProfiler`, i.e. platewise data-sets, where every file describes a single features for single cells.
* Parse the downloaded data using `rnaiparser`: install the package, and process as described in the package folder.
This generates a list of raw `tsvs` files or a bundled `h5` file. Until now the parser writes featuresets for `cells`, `perinuclei`, `nuclei`,  `expandednuclei`,  `bacteria` and `invasomes`.
* Finally cells can be queried using `rnaiquery`. For that first meta files generated from the step above are written into a database. Then the DB can be queried against to subset single genes, sirnas, pathogens, etc. efficiently.

## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@bsse.ethz.ch">simon.dirmeier@bsse.ethz.ch</a>

The `tix_parser` combines several subpackages for parsing tix matlab files
into tsvs:

### Run

Run the complete thing with:

```sh
  pip install -r requirements.txt
  python run_all.py ...
```

If you get errors, I probably forgot some dependency.
Just email me to noreply@simon-dirmeier.net




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