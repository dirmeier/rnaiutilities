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


import abc
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseConnection(metaclass=abc.ABCMeta):

    def __init__(self):
        self._connection = None

    def close(self):
        logger.info("Closing connection to db")
        self._connection.close()

    @abc.abstractmethod
    def query(self, q):
        pass

    @abc.abstractmethod
    def execute(self, statement):
        pass

    @abc.abstractmethod
    def insert_many(self, many, tab):
        pass

    @abc.abstractmethod
    def insert_elements(self, file, meta, f):
        pass

    @abc.abstractmethod
    def exists(self, tab):
        pass
