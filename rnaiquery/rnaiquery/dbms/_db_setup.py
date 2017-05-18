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


import logging
import os
import yaml

from rnaiquery.globals import FEATURECLASS, FEATURES, ELEMENTS
from rnaiquery.globals import FILE_FEATURES_PATTERNS
from rnaiquery.globals import GENE, SIRNA, WELL, LIBRARY, DESIGN
from rnaiquery.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseInserter:
    _gsw_ = [GENE, SIRNA, WELL]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def insert(self, path):
        self._create_dbs()
        fls = list(
          filter(
            lambda x: x.endswith("_meta.tsv"), [f for f in os.listdir(path)]
          )
        )
        le = len(fls)
        for i, file in enumerate(fls):
            if i % 100 == 0:
                logger.info("Doing file {} of {}".format(i, le))
            self._insert(path, file)
        self._create_indexes()

    def _insert(self, path, file):
        filename = os.path.join(path, file)
        try:
            # parse file name meta information
            ma = FILE_FEATURES_PATTERNS.match(file.replace("_meta.tsv", ""))
            stu, pat, lib, des, ome, rep, pl, feature = ma.groups()
            self._insert_file_suffixes(
              filename, stu, pat, lib,
              des, rep, pl, feature
            )

            # read the meta file
            with open(filename, "r") as fh:
                meta = yaml.load(fh)
            self._insert_meta(filename, meta)

        except ValueError as e:
            logger.error("Could not match meta file {} and value {}"
                         .format(file, e, file))

    def _insert_file_suffixes(self, file, study, bacteria, library,
                              design, replicate, plate, featureclass):
        ins = self._insert_meta_into_statement(
          file, study, bacteria, library, design,
          replicate, plate, featureclass
        )
        self.__connection.execute(ins)

    @staticmethod
    def _insert_meta_into_statement(
      file, study, bacteria, library,
      design, replicate, plate, featureclass):
        return "INSERT INTO meta " \
               "({}, {}, {}, {}, {}, {}, {}, {}) ".format(STUDY,
                                                          PATHOGEN,
                                                          LIBRARY,
                                                          DESIGN,
                                                          REPLICATE,
                                                          PLATE,
                                                          FEATURECLASS,
                                                          "filename") + \
               "VALUES (" + \
               "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(study,
                                                                         bacteria,
                                                                         library,
                                                                         design,
                                                                         replicate,
                                                                         plate,
                                                                         featureclass,
                                                                         file)

    def _insert_meta(self, file, meta):
        self._insert_elements(file, meta[ELEMENTS])
        self._insert_features(file, meta[FEATURES])

    def _insert_elements(self, file, meta):
        self.__connection.insert_elements(
          file,
          meta,
          self._insert_into_statement)

    def _insert_features(self, file, meta):
        tab = file.replace("_meta.tsv", "").split("/")[-1].replace("-", "_")
        if not self._exists(tab):
            self._create_file_feature_table(tab)
            self.__connection.insert_many(meta, tab)

    def _create_dbs(self):
        self.__connection.execute(self._create_meta_table())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_name(col)
            self.__connection.execute(tb)

    @staticmethod
    def _create_meta_table():
        s = "CREATE TABLE IF NOT EXISTS meta " + \
            "(" + \
            "id serial, "
        for col in DatabaseInserter._descr_:
            s += "{} varchar(100) NOT NULL, ".format(col)
        s += "filename varchar(1000) NOT NULL, " + \
             "PRIMARY KEY(id)" + \
             ");"
        logger.info(s)
        return s

    @staticmethod
    def _create_table_name(t):
        s = "CREATE TABLE IF NOT EXISTS {} ".format(t) + \
            "(" + \
            "id serial, " + \
            "{} varchar(100) NOT NULL, ".format(t) + \
            "filename varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(id)" + \
            ");"
        logger.info(s)
        return s

    def _create_indexes(self):
        self.__connection.execute(self._create_meta_index())
        for col in [GENE, SIRNA, WELL]:
            tb = self._create_table_index(col)
            self.__connection.execute(tb)

    @staticmethod
    def _create_meta_index():
        s = "CREATE INDEX meta_index ON meta ({});" \
            .format(", ".join(DatabaseInserter._descr_))
        logger.info(s)
        return s

    @staticmethod
    def _create_table_index(t):
        s = "CREATE INDEX {}_index ON {} ({});".format(t, t, t)
        logger.info(s)
        return s

    def _create_file_feature_table(self, tab):
        s = "CREATE TABLE IF NOT EXISTS {}".format(tab) + \
            " (feature varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(feature));"
        self.__connection.execute(s)

    def _exists(self, tab):
        ex = self.__connection.exists(tab)
        return ex

    @staticmethod
    def _insert_into_statement(k, v, file):
        s = "INSERT INTO {} ({}, filename) VALUES('{}', '{}')" \
            .format(k, k, v, file)
        return s
