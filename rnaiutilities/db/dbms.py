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

import logging
import os
import re
import sys
from itertools import chain

from rnaiutilities.db.db_query_builder import DatabaseQueryBuilder
from rnaiutilities.db.postgres_connection import PostgresConnection
from rnaiutilities.db.sqlite_connection import SQLiteConnection
from rnaiutilities.db.utility import feature_table_name
from rnaiutilities.filesets.table_file_set import TableFileSet
from rnaiutilities.globals import GENE, SIRNA, WELL
from rnaiutilities.utility.files import filter_files, read_yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DBMS:
    """
    Class for opening and working with data bases.
    """

    _SQLITE_ = "sqlite"
    _FILE_FEATURES_REGEX_ = re.compile(
      "(\w+)-(\w+)-(\w+)-(\w+)-(\w+)-(\d+)-(.*)_(\w+)")

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

    def tableset(self, file_name=None, **kwargs):
        """
        Query the database and compose a dataset filtered by **kwargs.

        :param file_name: a preprocessed file that has already been used vor
         querying using `query`. If file_name is not none the file is used for
         creating the return argument, otherwise a complete database query is
         submitted.
        :param kwargs: a keyword argument of filtering criteria or None.
        :return: returns a list table file sets
        :rtype: list(TableFileSet)
        """

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
        # parses sth like: '(i_am_a_plate)_someText_meta.tsv'
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
            query = DatabaseQueryBuilder().build_query(**kwargs)
            results = self.__connection.query(query)
        else:
            results = DatabaseQueryBuilder().read_query_file(file_name)
        return results

    def query(self, **kwargs):
        return self._query(file_name=None, **kwargs)

    def insert(self, path):
        """
        Insert meta information from parsed imaging data into a database.
        Creates a couple of different databases for all created meta files
        containing information about plates, filenames, siRNAs, genes, etc.

        :param path: the path where the parsed files are placed
        :return: str
        """

        self._insert(path)

    def _insert(self, path):
        d = DatabaseQueryBuilder()
        self._create_tables(d)
        self._insert_files(path, d)
        self._create_indexes(d)

    def _create_tables(self, d):
        # creates meta file database
        # also creates one table for every plate and feature type
        self.__connection.execute(d.create_meta_table_statement())
        for col in [GENE, SIRNA, WELL]:
            tb = d.create_table_name(col)
            self.__connection.execute(tb)

    def _insert_files(self, path, d):
        fls = filter_files(path, "_meta.tsv")
        for i, file in enumerate(fls):
            if i % 100 == 0:
                logger.info("Doing file {} of {}".format(i, len(fls)))
            self._insert_file(d, path, file)

    def _insert_file(self, d, path, file):
        filename = os.path.join(path, file)
        try:
            ma = DBMS._FILE_FEATURES_REGEX_.match(file.replace("_meta.tsv", ""))
            stu, pat, lib, des, _, rep, pl, feature = ma.groups()
            # put the file classifier suffixes into the meta database
            # this really only regards the NAME of the file, the FEATURE it
            # is containing and the meta that describes the plate
            ins = d.create_into_meta_statement(
              filename, stu, pat, lib, des, rep, pl, feature)
            self.__connection.execute(ins)
            # read the meta file and put the meta plate information
            # (genes, sirnas) into the database for the plate
            meta = read_yaml(filename)
            self.__connection.insert_elements(
              file, meta, d.insert_into_statement)
            tab = feature_table_name(file)
            if not self.__connection.exists(tab):
                s = d.create_file_feature_table(tab)
                self.__connection.execute(s)
                self.__connection.insert_many(meta, tab)
        except ValueError:
            logger.error("Could not match meta file {}".format(file))

    def _create_indexes(self, d):
        self.__connection.execute(d.create_meta_index())
        for col in [GENE, SIRNA, WELL]:
            tb = d.create_table_index(col)
            self.__connection.execute(tb)

    def select(self, select, **kwargs):
        q = DatabaseQueryBuilder().build_select_query(select, **kwargs)
        return map(lambda x: x[0], self.__connection.query(q))
