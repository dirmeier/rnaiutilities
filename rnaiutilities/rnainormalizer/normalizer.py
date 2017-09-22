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
import re
import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Normalizer:
    _nf_ = ["zscore"]

    def __init__(self, *args):
        """
        Constructor for Normalizer.

        :param *args: a tuple of normalisation functions
        :type *args: tuple(str)
        """

        if any(arg not in Normalizer._nf_ for arg in args):
            raise ValueError("Please select only functions: {}"
                             .format("/".join(Normalizer._nf_)))
        self._normalize = list(args)

    def normalize(self, file_name):
        """
        Normalize on plates from a file generated from `rnai-parse parse`.

        :param file_name: file to be parsed
        :type file_name: str
        """

        outfile = self._outfile(file_name)
        lines, prefix = [None] * 100000, None
        header, dat = [], []
        run = 0
        # iterate over file and normalize data.
        # write normalized data to new file
        with open(file_name, "r") as fr, open(outfile, "w") as fw:
            logger.info("Normalizing file {}".format(file_name))
            for line in fr.readlines():
                st = line.rstrip().split("\t")
                # first line
                if line.startswith("study"):
                    header = st
                    self._write(fw, st, True)
                    continue
                # this starts a new plate
                elif lines[0] is None or not line.startswith(prefix):
                    # first batch of data (a plate) is ready to be normalized
                    if lines[0] is not None and not line.startswith(prefix):
                        dat = self._normalize_plate(lines[:run], header)
                        self._write(fw, dat, False)
                        # continue with next batch by setting all to zero, None
                        lines, prefix, run = [None] * 100000, None, 0
                    prefix = "\t".join(st[:6])
                # add lines to the array until the current plate has passed
                # preallocated size suffices
                if run < len(lines):
                    lines[run] = st
                    run += 1
                # append otherwise (should not happen)
                else:
                    lines.append(st)
            # do normalization of last batch of data that has not been handled
            dat = self._normalize_plate(lines[:run], header)
            self._write(fw, dat, False)
            logger.info("Finished normalizing.")

    @staticmethod
    def _write(filehandle, arr, is_header):
        if is_header:
            filehandle.write("\t".join(arr) + "\n")
        else:
            for el in arr:
                filehandle.write("\t".join(map(lambda x: str(x), el)) + "\n")

    def _normalize_plate(self, lines, header):
        df, feature_columns = self._to_pandas(lines, header)
        # do normalisations on the fly
        for normal in self._normalize:
            f = self.__getattribute__("_" + normal)
            df, well_df = f(df, None, feature_columns)

        return df.values.tolist()

    @staticmethod
    def _zscore(df, well_df, feature_columns):
        for col in feature_columns:
            df[col] = (df[col] - numpy.nanmean(df[col], )) / \
                      (numpy.nanstd(df[col]) + 0.00000001)
        return df, well_df

    @staticmethod
    def _outfile(file_name):
        out_reg = re.match("(.+)\.(\w+)", file_name)
        return out_reg.group(1) + "_normalize." + out_reg.group(2)


    @staticmethod
    def _to_pandas(lines, header):
        df = pandas.DataFrame(lines, columns=header)
        feature_columns = list(filter(
          lambda x: any(x.startswith(f) for f in ["cells", "perinu", "nuclei"]),
          df.columns))
        df[feature_columns] = df[feature_columns].apply(pandas.to_numeric)

        return df, feature_columns
