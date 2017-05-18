# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17.05.17


import logging
import sqlite3

from rnaiquery.dbms._database_connection import DatabaseConnection
from rnaiquery.globals import GENE, SIRNA, WELL

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class SQLiteConnection(DatabaseConnection):

    def __init__(self, path):
        super().__init__()
        logger.info("Connecting to sqlitr db")
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
                logger.error("Could not match element {} and error {}"
                             .format(element, e))
        cursor.close()
        self._connection.commit()

    def exists(self, tab):
        s = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'" \
            .format(tab)
        bol = self.query(s)
        return True if len(bol) > 0 else False
