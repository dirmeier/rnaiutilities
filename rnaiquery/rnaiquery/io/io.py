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


import h5py
import pandas


class IO:
    _flat_ = "tsv"
    _h5_ = "h5"

    def __init__(self, f):
        if f is None:
            self._format = None
        else:
            self._format = IO._flat_ if f.endswith(IO._flat_) else  IO._h5_
        self._filename = f
        self._fh, self._dataset = None, None
        self._print_header = True

    def __enter__(self):
        self._print_header = True
        if self._format is not None and self._format == IO._h5_:
            self._fh = pandas.HDFStore(self._filename, complevel=9, complib='bzip2')
        else:
            raise ValueError("Not implemented yet")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._format == IO._h5_:
            self._fh.close()

    def dump(self, df):
        if not isinstance(df, pandas.DataFrame):
            raise TypeError("Please provide a resultset object")
        if self._format is None or self._format == IO._flat_:
            self._to_tsv(df)
        elif self._format == IO._h5_:
            self._to_h5(df)
        else:
            raise ValueError("What?")

    def _to_h5(self, df):
        # TODO
        self._fh.append(key="data", value=df)

    def _to_tsv(self, data):
        if self._format is None:
            print(
              data.to_csv(
                self._format,
                sep="\t",
                header=self._print_header,
                index=False
              )
            )
        else:
            data.to_csv(
              self._format,
              sep="\t",
              mode="a",
              header=self._print_header,
              index=False
            )
        self._print_header = False
