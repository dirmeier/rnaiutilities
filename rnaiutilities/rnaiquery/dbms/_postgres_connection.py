# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17.05.17

import logging

import psycopg2

from ._database_connection import DatabaseConnection
from ..globals import GENE, SIRNA, WELL

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class PostgresConnection(DatabaseConnection):
    def __init__(self):
        super().__init__()
        logger.info("Connecting to postgres db")
        self._connection = psycopg2.connect(database="tix")

    def query(self, q):
        with self._connection.cursor() as cursor:
            cursor.execute(q)
            res = cursor.fetchall()
        self._connection.commit()
        return res

    def execute(self, statement):
        with self._connection.cursor() as cursor:
            cursor.execute(statement)
        self._connection.commit()

    def insert_many(self, many, tab):
        with self._connection.cursor() as c:
            for x in many:
                c.execute("INSERT INTO {} VALUES ('{}')".format(tab, x))
        self._connection.commit()

    def insert_elements(self, file, meta, f):
        with self._connection.cursor() as cursor:
            for element in meta:
                try:
                    well, gene, sirna = element.split(";")[:3]
                    for k, v in {WELL: well, GENE: gene, SIRNA: sirna}.items():
                        ins = f(k, v, file)
                        cursor.execute(ins)
                except ValueError as e:
                    logger.error("Could not match element {} and error {}"
                                 .format(element, e))
        self._connection.commit()

    def exists(self, tab):
        s = "SELECT EXISTS(SELECT * FROM information_schema.tables" \
            " WHERE table_name = '{}');".format(tab)
        bol = self.query(s)
        return bol[0][0]

