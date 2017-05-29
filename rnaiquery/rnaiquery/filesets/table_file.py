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


class TableFile:
    def __init__(self, query_result, features, **kwargs):
        f = query_result[-1].replace("_meta.tsv", "")
        self._filename = f + "_data.tsv"
        self._feature_class = f.split("_")[-1]
        self._filesuffix = f.split("/")[-1]
        self._feature_list_table = self._filesuffix.replace("-", "_")
        self._features = set(features)
        self._filter = kwargs
        self._study, self._pathogen, self._lib, \
          self._design, self._replicate,\
          self._plate = query_result[1:7]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Tablefile: " + self._feature_list_table

    def __eq__(self, other):
        if not isinstance(other, TableFile):
            return False
        return self._filename == other._filename

    def __hash__(self):
        return hash(self._filename)


    @property
    def features(self):
        return self._features

    @property
    def filename(self):
        return self._filename

    @property
    def feature_class(self):
        return self._feature_class

    @property
    def filesuffix(self):
        return self._filesuffix

    @property
    def study(self):
        return self._study

    @property
    def pathogen(self):
        return self._pathogen

    @property
    def library(self):
        return self._lib

    @property
    def design(self):
        return self._design

    @property
    def replicate(self):
        return self._replicate

    @property
    def plate(self):
        return self._plate