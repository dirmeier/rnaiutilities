# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of rnaiquery.
#
# rnaiquery is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rnaiquery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rnaiquery. If not, see <http://www.gnu.org/licenses/>.
#
#
# @author = 'Simon Dirmeier'
# @email = 'mail@simon-dirmeier.net'

import sys
import logging
import pandas
import pathlib

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class IO:
    _flat_ = "tsv"
    _h5_ = "h5"

    def __init__(self, f):
        if f is None:
            logger.info("Writing to stdout")
            self._format = None
        else:
            out = IO._flat_ if f.endswith(IO._flat_) else IO._h5_
            logger.info("Writing to {} ".format(out))
            if pathlib.Path(f).is_file():
                logger.error(
                  "File {} already exists. Please delete/rename the file first to avoid erroneously overwriting.")
                sys.exit(-1)
            self._format = out
        self._filename = f
        self._fh, self._dataset = None, None
        self._print_header = True

    def __enter__(self):
        self._print_header = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dump(self, df, filesuffix):
        if not isinstance(df, pandas.DataFrame):
            raise TypeError("Please provide a resultset object")
        if self._format is None or self._format == IO._flat_:
            self._to_tsv(df)
        elif self._format == IO._h5_:
            self._to_h5(df, filesuffix)
        else:
            raise ValueError("What?")

    def _to_h5(self, df, filesuffix):
        df.to_hdf(self._filename, filesuffix)

    def _to_tsv(self, data):
        if self._format is None:
            print(
              data.to_csv(
                None,
                sep="\t",
                header=self._print_header,
                index=False
              )
            )
        else:
            if pathlib.Path(self._filename).is_file():
                self._print_header = False
            data.to_csv(
              self._filename,
              sep="\t",
              mode="a",
              header=self._print_header,
              index=False
            )
        self._print_header = False
