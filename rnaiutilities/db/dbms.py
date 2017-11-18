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


import sys
import logging

from rnaiutilities.db.db_query import DatabaseQuery
from rnaiutilities.db.db_setup import DatabaseInserter
from rnaiutilities.db.postgres_connection import PostgresConnection
from rnaiutilities.db.sqlite_connection import SQLiteConnection

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

    def query(self, file_name, **kwargs):
        # TODO: this needs changing,
        # separate the two things
        q = DatabaseQuery(self.__connection)
        return q.query(file_name, **kwargs)

    def print(self, **kwargs):
        # TODO: this needs changing
        q = DatabaseQuery(self.__connection)
        return q.print(**kwargs)

    def insert(self, path):
        # TODO: this needs changing
        d = DatabaseInserter(self.__connection)
        d.insert(path)

    def select(self, select, **kwargs):
        # TODO: this needs changing
        q = DatabaseQuery(self.__connection)
        return q.select(select, **kwargs)
