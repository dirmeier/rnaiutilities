rnaiutilities
=============

``rnaiutilities`` is a colelction of python scripts and modules for working
with image-based RNAi perturbation data. So far it has two functionalities

* ``rnai-parse`` for parsing CellProfiler matlab files,
* ``rnai-query`` for inserting meta information to a database, building datasets and selecting meta information from the DB.

rnai-parse
----------

``rnai-parse`` parses matlab files of CellProfiler features as raw ``tsvs``
or ``h5`` files. First you need to create a CONFIG file in ``yaml`` format
like this:

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
Check out the ``data`` folder in the main repository for some example datasets.

As a first step it makes sense to check if all kinome and genomes plates from
your meta plate file exist, i.e. have been downloaded:

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

The **parsed** files can be used for quickly subsetting the complete dataset.
For that first a database with meta files has to be setup. For that you can
either use ``postgres`` or ``sqlite``. So either

* start ``postgres`` with a database called ``tix`` and make it listen to port 5432,
* or provide a filename to the script and we use it as an stand-alone ``sqlite`` database (use a filename with suffix ``.db``).

For postgres run:

.. code-block:: bash

  rnai-query insert /i/am/a/path/to/parsed/data

For sqlite:

.. code-block:: bash

  rnai-query insert --db /i/am/a/file/called/tix.db /i/am/a/path/to/parsed/data

Where ``/i/am/a/path/to/parsed/data`` points to the folder where the ``*meta.tsv`` and ``*data.tsv`` files lie (the result from parsing).

Having the database set up, we can query for custom features, for example:

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

Checking the data-set content can be done using ``rnai-query select``. For
example:

.. code-block:: bash

   rnai-query select gene

The complete list of options is shown on the commandline.

There are probably still bugs, so patches are welcome.