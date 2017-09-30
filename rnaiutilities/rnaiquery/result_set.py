# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of rnaiutilities.
#
# rnaiutilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rnaiutilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rnaiutilities. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging
import os

import numpy as np
import pandas

from rnaiutilities.rnaiquery.filesets.table_file_set import TableFileSet
from rnaiutilities.rnaiquery.globals import WELL, GENE, SIRNA, \
    SAMPLE, ADDED_COLUMNS_FOR_PRINTING
from rnaiutilities.rnaiquery.io.io import IO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ResultSet:
    """
    Set of results derived from a database query.

    """

    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]
    _sar_ = ".*"

    def __init__(self, tablefile_sets, sample, **kwargs):
        self._tablefile_sets = tablefile_sets
        self._print_header = True
        self._filters = self._set_filter(**kwargs)
        self._sample = sample if sample is not None else 2 ** 30
        self._filter_fn = lambda x: x.loc[np.random.choice(
          x.index, self._sample, False), :] if len(x) >= self._sample else x
        # TODO: this is solved so badly
        self._shared_features = self._get_shared_features()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._tablefile_sets)

    def __iter__(self):
        for tablefileset in self._tablefile_sets:
            yield tablefileset

    def dump(self, fh=None):
        """
        Print the result set of the database query to tsv or stdout. If a string
        is given as param *fh* prints to file, otherwise if None is given prints
        to stdout.

        :param fh: either str or None(default)
        """
        with IO(fh) as io:
            for tablefileset in self._tablefile_sets:
                self._dump(tablefileset, io)
        logger.info("Successfully wrote table files!")

    def _dump(self, tablefileset, io):
        """
        Dumbs a table file to tsv/h5/stdout

        This is arguably not very efficient, since it first reads a tsv, then
        does filtering, grouping and sampling and then prints to tsv again.
        For the time being this suffices.

        Ideally at some point Nicolas' DB is used.

        """

        # test if the data files can be found
        if all(os.path.isfile(f) for f in tablefileset.filenames):
            # read the data files, i.e. cells/nuclei/perinuclei
            data = self.read(tablefileset)
            if data is None:
                return
            # only take subset of columns that every thingy has
            # additionally return the columns in order to check for bad format
            data, feat_cols = self._get_columns(
              data, tablefileset.feature_classes)
            if len(feat_cols) != len(self._shared_features):
                logger.warning(
                  "{} does not have the correct number of features. Skipping."
                      .format(tablefileset.filenames))
                return
            # filter on well/sirna/gene
            data = self._filter_data(data)
            if len(data) == 0:
                return
            # sample from each gene/sirna/well group if wanted
            data = self._sample_data(data)
            # append study/pathogen/library/..
            data = self._append_to_data(data, tablefileset)
            io.dump(data, tablefileset.filesuffixes)
        else:
            logger.warning("Could not find files: {}"
                           .format(", ".join(tablefileset.filenames)))

    def read(self, tablefileset):
        """
        Read the table files from a plate and concatenate the single tables.
        Since the dimensions of the tables should be the same, the concatenation
         should work. If the dimensions do not fit (i.e. the mapping did not
         work), `None` is returned.

        :param tablefileset: the object to be parsed
        :type tablefileset: TableFileSet

        :return: returns the merged data as dataframe or None if the concat did
         not work
        :rtype: pandas.DataFrame
        """

        if not isinstance(tablefileset, TableFileSet):
            raise ValueError("Provide a TableFileSet object.")
        # read the X files to memory
        tables = [
            pandas.read_csv(f, sep="\t", header=0)
            for f in tablefileset.filenames
        ]
        # check if the dimensions of the tables are the same
        if not self._tables_have_correct_shapes(tables, tablefileset):
            return None
        # iterate over the tables and drop the redundant meta information
        tables = self._drop_meta_columns(tables, tablefileset)
        if tables is None:
            return None
        # merge the three tables together column-wise
        data_merged = pandas.concat(tables, axis=1)
        return data_merged

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

    @staticmethod
    def _append_to_data(data, table):
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
                    reg = "^" + "|".join(v.split(",")) + "$"
                    # user provided gene/sirna/well regex to match
                    self.__setattr__("_" + k, reg)
                else:
                    # if user didnt provide anything match all
                    self.__setattr__("_" + k, ResultSet._sar_)
                fls.append(v)
        return fls

    def _get_shared_features(self):
        # suppose one plate does not have cells/nuclei/perinuclei?
        # this messes up the whole featureset

        # TODO: check for all three (cells/nuclei/perinuclei) feature classes
        # here??? This would remove some plates.
        features_set = set()
        for tablefile in self._tablefile_sets:
            if not features_set:
                features_set |= tablefile.features
            else:
                features_set &= tablefile.features
        # add all required columns that we most definitely want to cell
        # does that make sense? i guess this introduces crap
        for feature_class, cols in ADDED_COLUMNS_FOR_PRINTING.items():
            for col in cols:
                add_col = feature_class + "." + col
                features_set.add(add_col)
        return sorted(list(features_set))

    def _get_columns(self, data, feature_classes):
        """
        Subset the dataframe for columns that are shared in all tablefile sets.
        """

        # get the columns in data that are feature columns
        feat_cols = set(self._get_feature_column_names(data, feature_classes))
        # get the columns that are meta columns, such as gene/well/etc.
        meta_cols = self._get_meta_column_names(data, feature_classes)
        # make sure to only take columns that are in the
        feat_cols = list(feat_cols & set(self._shared_features))
        # get the new data
        data = data[meta_cols + feat_cols]
        # add features that are explicitely desired
        # but not found in every screen :(
        for feature_class in feature_classes:
            if feature_class in ADDED_COLUMNS_FOR_PRINTING:
                for col in ADDED_COLUMNS_FOR_PRINTING[feature_class]:
                    add_col = feature_class + "." + col
                    if add_col not in data:
                        # add the new column
                        data.insert(len(data.columns), add_col, 0)
                        # add the column to the new feature set for later check
                        feat_cols.append(add_col)
        # sort columns (this should be a sufficient condition
        # for optimal overlap)
        feat_cols = sorted(feat_cols)
        # reindex the data set
        data = data.reindex_axis(meta_cols + feat_cols, axis=1, copy=False)
        return [data, feat_cols]

    @staticmethod
    def _get_feature_column_names(data, feature_classes):
        """
        Get feature column names.
        """

        feat_cols = list(
          filter(lambda x: any(x.startswith(f) for f in feature_classes),
                 data.columns))
        return feat_cols

    @staticmethod
    def _get_meta_column_names(data, feature_classes):
        """
        Get meta column names.
        """

        meta_cols = list(
          filter(lambda x: not any(x.startswith(f) for f in feature_classes),
                 data.columns))
        return meta_cols

    @staticmethod
    def _tables_have_correct_shapes(tables, tablefileset):
        for i in range(len(tables) - 1):
            for j in range(i + 1, len(tables)):
                if tables[i].shape[0] != tables[j].shape[0]:
                    logger.error("TableFileSet's {} data files do not "
                                 "have matching dimensions."
                                 .format(tablefileset.classifier))
                    return False
        return True

    def _drop_meta_columns(self, tables, tablefileset):
        # get meta column names
        meta_cols = self._get_meta_column_names(
          tables[0], tablefileset.feature_classes)
        # iterate over the plate meta columns and drop them from the tables
        for i in range(1, len(tables)):
            meta_cols_curr = self._get_meta_column_names(
              tables[i], tablefileset.feature_classes)
            if meta_cols != meta_cols_curr:
                logger.error("Meta column names are not equal: {}"
                             .format(tablefileset))
                return None
            feat_col_names = self._get_feature_column_names(
              tables[i], tablefileset.feature_classes)
            tables[i] = tables[i][feat_col_names]

        return tables
