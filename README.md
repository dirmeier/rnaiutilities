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
