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


from rnaiutilities.rnaiquery.db import DBMS


class TableFileSets:
    def __init__(self, db=None):
        self._db = db
        # map of maps that hold file pointers
        # map - (1:n) -> [_gene_map , ...] - (1:m) -> filename
        self._file_set = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "TODO"

    def print(self, **kwargs):
        with DBMS(self._db) as d:
            res = d.print(**kwargs)
        return res

    def filter(self, **kwargs):
        """
        Get a set of files that meets some criteria. Kwargs is a names list,
        that can have the following form:

         {
                study="infectx",
                pathogen="salmonella",
                well="a01",
                gene="tp53",
                sirna="blub",
                replicate=1,
                library="d"
         }

        :return: returns a set of TableFile
        :rtype: set(TableFile)
        """

        with DBMS(self._db) as d:
            res = d.query(**kwargs)
        return res


