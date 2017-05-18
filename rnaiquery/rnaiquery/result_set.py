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

from rnai_query.globals import WELL, GENE, SIRNA, SAMPLE

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class ResultSet:
    _filter_attributes_ = [GENE, SIRNA, WELL, SAMPLE]
    _sar_ = ".*"

    def __init__(self, files, sample, **kwargs):
        self._tablefile_set = files
        self._sample = sample
        self._print_header = True
        self._filters = self._set_filter(**kwargs)
        self._filter_fn = lambda x: x.loc[np.random.choice(
          x.index, self.__getattribute__("_" + SAMPLE), False), :]

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
        self._print_header = True
        for tablefile in self._tablefile_set:
            self._dump(fh, tablefile)
        logger.info("Successfully wrote table files!")

    def _dump(self, fh, tablefile):
        """
        Dumbs a table file to tsv. 
         
        This is arguably not very efficient, since it first reads a tsv, then 
        does filtering, grouping and sampling and then prints to tsv again.
        For the time being this suffices.
        
        Ideally at some point Nicolas' DB is used.
        
        """

        # test if the data file can be found
        if os.path.isfile(tablefile.filename):
            # read the data file
            data = pandas.read_csv(tablefile.filename, sep="\t", header=0)
            # filter on well/sirna/gene
            data = self._filter_data(data)
            if len(data) == 0:
                return
            # sample from each gene/sirna/well group if wanted
            data = self._sample_data(data)
            # append study/pathogen/library/..
            data = self._append_to_data(data, tablefile)
            self._to_tsv(data, fh)
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

    def _to_tsv(self, data, fh):
        if fh is None:
            print(
              data.to_csv(fh, sep="\t", header=self._print_header, index=False))
        else:
            data.to_csv(
              fh, sep="\t", mode="a", header=self._print_header, index=False)
        self._print_header = False
