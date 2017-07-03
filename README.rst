*************
rnaiutilities
*************

A collection of python modules and command line toole for processing image-based RNAi screens.

Introduction
============

`rnaiutilies` provide a set of python modules that can be used to process, convert, query and analyse imaged-based RNAi-screens.

The packages are designed for the following workflow:

* Download raw `mat` files from an openBIS instance or where ever your data lie. The `mat` files are supposed to be created by `CellProfiler`, i.e. platewise data-sets, where every file describes a single features for single cells.
* Parse the downloaded data using `rnai-parse`: install the package, and process as described in the package folder. This generates a list of raw `tsvs` files or a bundled `h5` file. Until now the parser writes featuresets for `cells`, `perinuclei`, `nuclei`,  `expandednuclei`,  `bacteria` and `invasomes`.
* Finally cells can be queried using `rnai-query`. For that first meta files generated from the step above are written into a database. Then the DB can be queried against to subset single genes, sirnas, pathogens, etc. efficiently.

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

With ``rnaiutilities`` first all matlab files are parsed and then queried by
meta information. Check out the documentation on ``docs``.

rnai-parse
----------

``rnai-parse`` parses matlab files of CellProfiler features as raw tsvs or h5
files. First you need to create a config file in ``yaml`` format like this:

.. code-block:: yaml

  layout_file: "/path/to/layout.tsv"
  plate_folder: "/path/to/plates"
  output_path: "/path/to/outfolder"
  plate_id_file: "/path/to/experiment_meta_file.tsv"
  multiprocessing: False


``layout_file`` describes the placement of siRNAs and genes on the plates,
``plate_folder`` points to the collection of matlab files, ``output_path`` is
the target directory where files are written to. ``plate_id_file`` is a list
of ids of plates that are going to be parsed in case only a subset of
``plate_folder`` should get parsed. ``multiprocessing`` is a boolean
determining whether python uses multiple processes or not.
Check out the ``data`` folder for some example datasets.

As a first step it makes sense to check if all kinome and genomes plates from
your meta plate file exist:

.. code-block:: bash

  rnai-parse checkdownload CONFIG

If the files are downloaded as intended, parse them to tsv:

.. code-block:: bash

  rnai-parse parse CONFIG

If parsing is complete, you can create a report if all files have been parsed
or if some are missing:

.. code-block:: bash

  rnai-parse report CONFIG

The result of the parsing process should be a set of files for every plate.
For example every plate should create ``*data.tsv`` files and a respective
``*meta.tsv`` for it.

rnai-query
----------

The parsed files can be used for quickly subsetting the complete dataset. For
that first a database with meta files has to be setup. For that you can
either use ``postgres`` or ``sqlite``. So either

* start ``postgres`` with a database called ``tix`` and make it listen to port 5432,
* or provide a filename to the script and we use it as an stand-alone ``sqlite`` database (use a filename with suffix ``.db``).

For postgres run:

.. code-block:: bash

  rnai-query insert /i/am/a/path/to/parsed/data

For sqlite:

.. code-block:: bash

  rnai-query insert --db /i/am/a/file/called/tix.db /i/am/a/path/to/parsed/data

Where ``/i/am/a/path/to/parsed/data`` points to the folder where the ``meta.tsv``s and ``data.tsv``s lie.

Having the database set up, we can query for custom features.

.. code-block:: bash

  rnai-query query --sample 10

In this case, since no DB is specified, we expect a postgres DB to be running.
The query would return 10 single cells randomly sampled from each well from
all plates.

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
database running.

The query should get all ``cell``-features where gene ``star`` has been
transturbed using ``dharmacon`` libraries. You can create the database (file)
yourself or just use mine.

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

If any argument is not set, i.e. set to ``None``, the whole database will be searched and no filters applied.

There are probably still bugs, so patches are welcome.

Author
======

- Simon Dirmeier <simon.dirmeier@bsse.ethz.ch>

.. _anaconda: https://www.continuum.io/downloads
.. _environment: https://conda.io/docs/using/envs.html
