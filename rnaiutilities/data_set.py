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


class DataSet:
    """
    Class representing any kind of tabular data set.
    Wraps a pandas data frame and offers different methods for reading,
    preprocessing and writing data.
    """

    def __init__(self, data, feature_columns, classifier):
        """
        Constructor of DataSet. Needs a pandas DataFrame and a list of strings
         representing the feature columns.

        :param data: a pandas dataframe
        :type data: pandas.DataFrame
        :param feature_columns: a list of strings names column names for the
         features
        :type feature_columns: list(str)
        """

        self.__data = data
        self.__feature_columns = feature_columns
        self.__classifier = classifier

    def __str__(self):
        return self.__classifier

    def __repr__(self):
        return self.__str__()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def feature_columns(self):
        return self.__feature_columns

    @feature_columns.setter
    def feature_columns(self, value):
        self.__feature_columns = value
