*************
rnaiutilities
*************

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :target: http://www.repostatus.org/#active
.. image:: https://travis-ci.org/cbg-ethz/rnaiutilities.svg?branch=master
   :target: https://travis-ci.org/cbg-ethz/dataframe/
.. image:: https://codecov.io/gh/cbg-ethz/dataframe/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cbg-ethz/dataframe
.. image:: https://api.codacy.com/project/badge/Grade/3787d3068c2f472bb337665ff67d7068
   :target: https://www.codacy.com/app/simon-dirmeier/dataframe?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dirmeier/dataframe&amp;utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/rnaiutilities/badge/?version=latest
   :target: http://rnaiutilities.readthedocs.io/en/latest/?badge=latest
   :alt: doc

A collection of python modules and command line tools for processing
image-based RNAi screens.

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

Documentation
=============

Check out the documentation in readthedocs_.

Author
======

- Simon Dirmeier <simon.dirmeier@bsse.ethz.ch>

.. _anaconda: https://www.continuum.io/downloads
.. _environment: https://conda.io/docs/using/envs.html
.. _readthedocs: https://rnaiutilities.readthedocs.io/en/latest/