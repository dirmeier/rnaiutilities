# rnaiutilities <img src="https://raw.githubusercontent.com/dirmeier/rnaiutilities/master/_fig/fig_single_cells.jpg" align="right" width="160px"/>

[![Project Status](http://www.repostatus.org/badges/latest/inactive.svg)](http://www.repostatus.org/#inactive)
[![Build](https://travis-ci.org/dirmeier/rnaiutilities.svg?branch=master)](https://travis-ci.org/dirmeier/rnaiutilities)
[![Coverage](https://codecov.io/gh/dirmeier/rnaiutilities/branch/master/graph/badge.svg)](https://codecov.io/gh/dirmeier/rnaiutilities)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/451bb1a5b6bb46a499713f048f296ed4)](https://www.codacy.com/app/simon-dirmeier/rnaiutilities?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dirmeier/rnaiutilities&amp;utm_campaign=Badge_Grade)
[![Documentation](https://readthedocs.org/projects/rnaiutilities/badge/?version=latest)](https://rnaiutilities.readthedocs.io/en/latest/?badge=latest)


A collection of python modules and command line tools for processing image-based RNAi screens.

## Introduction

`rnaiutilities` provide a set of python modules and commandline scripts that can be used to process, convert, query and analyse imaged-based RNAi-screens.

The packages are designed for the following workflow:

* Download raw `mat` files from an openBIS instance or where ever your data lie. The `mat` files are supposed to be created by `CellProfiler`, i.e. platewise data-sets, where every file describes a single features for single-cells.
* Parse the downloaded data using `rnai-parse`: install the package, and process as described in the package folder. This generates a list of raw `tsv`s files or a bundled `h5` file. Until now the parser writes featuresets for *cells*, *perinuclei*, *nuclei*, *expandednuclei*,  *bacteria* and *invasomes*.
* Query the meta DB using ``rnai-query`` and create and combine datasets. For that first meta files generated from the step above are written into a database. Then the DB can be queried against to subset single *genes*, *sirnas*, *pathogens*, etc. and write the *normalized* results.

## Installation

Make sure to have `python3` installed. `rnaiutilities` does not support
previous versions. The best way to do that is to download [anaconda](https://www.continuum.io/downloads) and create a
virtual [environment](https://conda.io/docs/using/envs.html).

Download the latest [release](https://github.com/dirmeier/rnaiutilities/releases) first and install it using:

```bash
  pip install .
```

If you get errors, I probably forgot some dependency.

## Documentation

Check out the documentation [here](https://rnaiutilities.readthedocs.io/en/latest/).

## Author

Simon Dirmeier <simon.dirmeier@web.de>

