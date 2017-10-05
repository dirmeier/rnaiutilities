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

import numpy
import pandas

from rnaiutilities.rnaiquery.globals import BSCORE, ZSCORE, LOESS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Normalizer:
    _nf_ = [ZSCORE]
    _normalisations_ = [BSCORE, ZSCORE, LOESS]

    def __init__(self, *args):
        """
        Constructor for Normalizer.

        :param *args: a tuple normalisation methods to use, e.g. like 'zscore'.
          Options so far are 'bscore', 'loess' and 'zscore'.
        :type *args: tuple(str)
        """

        self._normalize = None
        if args:
            self.set_normalization(*args)

    def set_normalization(self, *args):
        """
        Set the normalisation methods.

        :param *args: a tuple normalisation methods to use, e.g. like 'zscore'.
          Options so far are 'bscore', 'loess' and 'zscore'.
        :type *args: tuple(str)
        """

        self._check_methods(*args)
        self._normalize = list(args)

    @staticmethod
    def _check_methods(*args):

        if any(arg not in Normalizer._nf_ for arg in args):
            raise ValueError(
              "Please select only functions: {}"
                .format("/".join(Normalizer._nf_)))

    def normalize_plate(self, data, feature_cols):
        """
        Normalize a plate.

        :param data: the data to normalize
        :type data: pandas.DataFrame
        :param feature_cols: the columns representing features
        :type feature_cols: list(str)
        """

        logger.info("Normalizing plate.")
        return self._normalize_plate(data, feature_cols)

    def _normalize_plate(self, df, feature_columns):
        df = self._replace_inf_with_nan(df, feature_columns)
        # do normalisations on the fly
        for normal in self._normalize:
            f = self.__getattribute__("_" + normal)
            df, well_df = f(df, None, feature_columns)

        return df

    @staticmethod
    def _replace_inf_with_nan(df, feature_columns):
        for col in feature_columns:
            idx = numpy.isinf(df[col])
            df.loc[idx, col] = numpy.nan
        return df

    @staticmethod
    def _zscore(df, well_df, feature_columns):
        logger.info("\tstandardizing feature columns.")
        for col in feature_columns:
            mea = numpy.nanmean(df[col])
            sd = numpy.nanstd(df[col])
            new_col_vals = (df[col] - mea) / (sd + 0.00000001)
            new_col_vals[numpy.isinf(new_col_vals)] = numpy.nan
            df[col] = new_col_vals
        return df, well_df
