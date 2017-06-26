# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of tix_query.
#
# tix_query is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tix_query is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tix_query. If not, see <http://www.gnu.org/licenses/>.
#
#
# @author = 'Simon Dirmeier'
# @email = 'mail@simon-dirmeier.net'


import logging
import os

import numpy as np
import pandas

from .globals import WELL, GENE, SIRNA, SAMPLE, \
    ADDED_COLUMNS_FOR_PRINTING
from .io.io import IO

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class ResultSet:
    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]
    _sar_ = ".*"

    def __init__(self, files, sample, **kwargs):
        self._tablefile_set = files
        self._print_header = True
        self._filters = self._set_filter(**kwargs)
        self._sample = sample if sample is not None else ((2 ** 31) - 1)
        self._filter_fn = lambda x: x.loc[np.random.choice(
          x.index, self._sample, False), :] if len(x) >= self._sample else x
        # TODO: this is solved so badly
        self._shared_features = self._get_shared_features()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._tablefile_set)

    def dump(self, fh=None):
        """
        Print the result set of the database query to tsv or stdout. If a string
        is given as param *fh* prints to file, otherwise if None is given prints
        to stdout.

        :param fh: either str or None(default)
        """
        with IO(fh) as io:
            for tablefile in self._tablefile_set:
                self._dump(tablefile, io)
        logger.info("Successfully wrote table files!")

    def _dump(self, tablefile, io):
        """
        Dumbs a table file to tsv/h5/stdout

        This is arguably not very efficient, since it first reads a tsv, then
        does filtering, grouping and sampling and then prints to tsv again.
        For the time being this suffices.

        Ideally at some point Nicolas' DB is used.

        """

        # test if the data file can be found
        if os.path.isfile(tablefile.filename):
            # read the data file
            data = pandas.read_csv(tablefile.filename,
                                   sep="\t",
                                   header=0)
            # only take subset of columns that every thingy has
            # additionally return the columns in order to check for bad format
            data, feat_cols = self._get_columns(data, tablefile.feature_class)
            if len(feat_cols) != len(self._shared_features):
                logger.warning(
                  "{} does not have the correct number of features. Skipping."
                      .format(tablefile.filename))
                return
            # filter on well/sirna/gene
            data = self._filter_data(data)
            if len(data) == 0:
                return
            # sample from each gene/sirna/well group if wanted
            data = self._sample_data(data)
            # append study/pathogen/library/..
            data = self._append_to_data(data, tablefile)
            io.dump(data, tablefile.filesuffix)
        else:
            logger.warning("Could not find file: {}".format(tablefile))

    def _filter_data(self, data):
        data = data[
            data.well.str.contains(self.__getattribute__("_" + WELL)) &
            data.gene.str.contains(self.__getattribute__("_" + GENE)) &
            data.sirna.str.contains(self.__getattribute__("_" + SIRNA))
            ]
        return data

    def _sample_data(self, data):
        if self.__getattribute__("_" + SAMPLE) != ResultSet._sar_:
            data = data.groupby([WELL, GENE, SIRNA]).apply(self._filter_fn)
        return data

    def _append_to_data(self, data, table):
        data.insert(0, "plate", table.plate)
        data.insert(0, "replicate", table.replicate)
        data.insert(0, "design", table.design)
        data.insert(0, "library", table.library)
        data.insert(0, "pathogen", table.pathogen)
        data.insert(0, "study", table.study)
        return data

    def _set_filter(self, **kwargs):
        fls = []
        for k, v in kwargs.items():
            if k in ResultSet._filter_attributes_:
                if v is not None:
                    # user provided gene/sirna/well regex to match
                    self.__setattr__("_" + k, v)
                else:
                    # if user didnt provide anything match all
                    self.__setattr__("_" + k, ResultSet._sar_)
                fls.append(v)
        return fls

    def _get_shared_features(self):
        features_set = set()
        for tablefile in self._tablefile_set:
            if not features_set:
                features_set |= tablefile.features
            else:
                features_set &= tablefile.features
        # add all required columns that we most definitely want to cell
        for feature_class, cols in ADDED_COLUMNS_FOR_PRINTING.items():
            for col in cols:
                add_col = feature_class + "." + col
                features_set.add(add_col)
        return sorted(list(features_set))

    def _get_columns(self, data, feature_class):
        # get the columns in data that are feature coluns
        feat_cols = set(
          filter(lambda x: x.startswith(feature_class), data.columns))
        # get the columns that are meta columns, such as gene/well/etc.
        meta_cols = list(
          filter(lambda x: not x.startswith(feature_class), data.columns))
        # make sure to only take columns that are in the
        feat_cols = list(feat_cols & set(self._shared_features))
        # get the new data
        data = data[meta_cols + feat_cols]
        # add features that are explicitely desired but not found in every screen :(
        if feature_class in ADDED_COLUMNS_FOR_PRINTING:
            for col in ADDED_COLUMNS_FOR_PRINTING[feature_class]:
                add_col = feature_class + "." + col
                if add_col not in data:
                    # add the new column
                    data.insert(len(data.columns), add_col, 0)
                    # add the column to the new feature set for later check
                    feat_cols.append(add_col)
        # sort columns
        feat_cols = sorted(feat_cols)
        # reindex the data set
        data = data.reindex_axis(meta_cols + feat_cols, axis=1, copy=False)
        return [data, feat_cols]
