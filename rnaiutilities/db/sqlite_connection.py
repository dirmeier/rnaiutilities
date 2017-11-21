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
import sqlite3

from rnaiutilities.db.database_connection import DatabaseConnection
from rnaiutilities.globals import GENE, SIRNA, WELL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SQLiteConnection(DatabaseConnection):
    def __init__(self, path):
        super().__init__()
        logger.info("Connecting to sqlite db")
        self._db_path = path
        self._connection = sqlite3.connect(self._db_path)

    def query(self, q):
        cursor = self._connection.cursor()
        cursor.execute(q)
        res = cursor.fetchall()
        cursor.close()
        self._connection.commit()
        return res

    def execute(self, statement):
        cursor = self._connection.cursor()
        cursor.execute(statement)
        cursor.close()
        self._connection.commit()

    def insert_many(self, many, tab):
        cursor = self._connection.cursor()
        for x in many:
            cursor.execute("INSERT INTO {} VALUES ('{}')".format(tab, x))
        cursor.close()
        self._connection.commit()

    def insert_elements(self, file, meta, f):
        cursor = self._connection.cursor()
        for element in meta:
            try:
                well, gene, sirna = element.split(";")[:3]
                for k, v in {WELL: well, GENE: gene,
                             SIRNA: sirna}.items():
                    ins = f(k, v, file)
                    cursor.execute(ins)
            except ValueError as e:
                logger.error(
                  "Could not match element {} and error {}".format(element, e))
        cursor.close()
        self._connection.commit()

    def exists(self, tab):
        s = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'" \
            .format(tab)
        bol = self.query(s)
        return True if len(bol) > 0 else False
