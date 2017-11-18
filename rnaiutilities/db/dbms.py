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

"""
Module related to all data base managment function, i.e., writing/selecting or
 opening DB connections.
"""
import re
import sys
import logging
from itertools import chain

from rnaiutilities.db.db_setup import DatabaseInserter
from rnaiutilities.db.db_query import DatabaseQueryBuilder
from rnaiutilities.db.postgres_connection import PostgresConnection
from rnaiutilities.db.sqlite_connection import SQLiteConnection
from rnaiutilities.db.utility import feature_table_name
from rnaiutilities.filesets.table_file_set import TableFileSet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DBMS:
    """
    Class for opening and working with data bases.
    """

    _SQLITE_ = "sqlite"

    def __init__(self, db=None):
        """
        Create an instance of a DBMS which allows opening a SQLite database
        connection and writing to it. The database parameter `db` should be
        a filename which stores the data base tables and indexes.

        :param db: the name of the data base to access or write, .e.g., 'db.db'
        :type db: str
        """
        self._db_path = db
        self.__connection = None
        if db is None:
            sys.exit("Set a database path.")
        else:
            self._db = DBMS._SQLITE_

    def __enter__(self):
        try:
            if self._db != DBMS._SQLITE_:
                self.__connection = PostgresConnection()
            else:
                self.__connection = SQLiteConnection(self._db_path)
        except Exception as e:
            sys.exit("Could not connect: " + str(e))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__connection.close()

    def tableset(self, file_name, **kwargs):
        results = self._query(file_name, **kwargs)
        tableset = self._compose_tableset(results, **kwargs)
        return tableset

    def _compose_tableset(self, results, **kwargs):
        plate_file_map = self._plate_file_map(results)
        # setup table file list
        fls = [
            TableFileSet(
              # the key, i.e. file prefix for all the data files
              # (so the name of the plate without feature suffix)
              k,
              # the table files that belong to one plate, i.e.
              # the different feature group files like cell/nuclei/perinuclei
              x,
              # chain lists of features to one list total
              list(chain.from_iterable(
                [self._feature_query(e[-1]) for e in x])),
              # filtering information
              **kwargs)
            for k, x in plate_file_map.items()
        ]

        return fls

    @staticmethod
    def _plate_file_map(results):
        # Set together the different feature files belonging to one plate.
        # I.e.: every plate has like 3 meta files, that belong together
        # like cell/nuclei/perinuclei
        result_set_map = {}
        reg = re.compile("(.+)_\w+_meta.tsv")
        for result in results:
            mat = reg.match(result[-1])
            if mat is not None:
                desc = mat.group(1)
                if desc not in result_set_map:
                    result_set_map[desc] = []
                result_set_map[desc].append(result)

        return result_set_map

    def _feature_query(self, filename):
        d = feature_table_name(filename)
        res = self.__connection.query("SELECT distinct * FROM {}".format(d))
        return list(map(lambda x: x[0], res))

    def _query(self, file_name, **kwargs):
        if not file_name:
            query = DatabaseQueryBuilder().build_query(file_name, **kwargs)
            results = self.__connection.query(query)
        else:
            results = DatabaseQueryBuilder().read_query_file(file_name)
        return results

    def print(self, **kwargs):
        # TODO: this needs changing
        q = DatabaseQueryBuilder(self.__connection)
        return q.print(**kwargs)

    def insert(self, path):
        # TODO: this needs changing
        d = DatabaseInserter(self.__connection)
        d.insert(path)

    def select(self, select, **kwargs):
        # TODO: this needs changing
        q = DatabaseQueryBuilder(self.__connection)
        return q.select(select, **kwargs)
