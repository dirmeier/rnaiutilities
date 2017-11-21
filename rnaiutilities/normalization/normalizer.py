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

import enforce
import numpy

from rnaiutilities.data_set import DataSet
from rnaiutilities.globals import BSCORE, ZSCORE, LOESS, NONE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Normalizer:
    _nf_ = [ZSCORE, NONE]
    _normalisations_ = [BSCORE, ZSCORE, LOESS, NONE]

    def __init__(self, *args):
        """
        Constructor for Normalizer.

        :param *args: a tuple normalisation methods to use, e.g. like 'zscore'.
          Options so far are 'bscore', 'loess' and 'zscore'.
        :type *args: tuple(str)
        """

        self._normalize = []
        if args:
            self.set_normalization(*args)

    def set_normalization(self, args):
        """
        Set the normalisation methods.

        :param args: a list if normalisation methods to use, e.g. like 'zscore'.
          Options so far are 'bscore', 'loess' and 'zscore'.
        :type args: list(str) or str
        """

        if not args:
            return
        if not isinstance(args, list):
            args = [args]
        self._check_methods(args)
        if NONE in args and len(args) > 1:
            raise ValueError(
              "You cannot use '{}' in combination with other normalisations {}"
              .format(NONE, "/".join(args)))
        if NONE not in list(args):
            self._normalize = list(args)

    @staticmethod
    def _check_methods(args):
        if any(arg not in Normalizer._nf_ for arg in args):
            raise ValueError(
              "Please select only functions: {}"
              .format("/".join(Normalizer._nf_)))

    @enforce.runtime_validation
    def normalize_plate(self, data: DataSet):
        """
        Normalize a plate.

        :param data: the data to normalize
        :type data: DataSet
        """

        logger.info("Normalizing plate.")
        return self._normalize_plate(data)

    def _normalize_plate(self, df):
        df = self._replace_inf_with_nan(df, df.feature_columns)
        # do normalisations on the fly
        for normal in self._normalize:
            f = self.__getattribute__("_" + normal)
            df, _ = f(df, None, df.feature_columns)
        return df

    @staticmethod
    def _replace_inf_with_nan(df, feature_columns):
        for col in feature_columns:
            idx = numpy.isinf(df.data[col])
            df.data.loc[idx, col] = numpy.nan
        return df

    @staticmethod
    def _zscore(df, well_df, feature_columns):
        logger.info("\tstandardizing feature columns.")
        for col in feature_columns:
            mea = numpy.nanmean(df.data[col])
            sd = numpy.nanstd(df.data[col])
            new_col_vals = (df.data[col] - mea) / (sd + 0.00000001)
            new_col_vals[numpy.isinf(new_col_vals)] = numpy.nan
            df.data[col] = new_col_vals
        return df, well_df
