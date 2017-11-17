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
import os

import yaml

from rnaiutilities.globals import FEATURECLASS, FEATURES, ELEMENTS
from rnaiutilities.globals import FILE_FEATURES_REGEX
from rnaiutilities.globals import GENE, SIRNA, WELL, LIBRARY, DESIGN
from rnaiutilities.globals import REPLICATE, PLATE, STUDY, PATHOGEN

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseInserter:
    _gsw_ = [GENE, SIRNA, WELL]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def insert(self, path):
        """
        Insert meta information from parsed imaging data into a database.
        Creates a couple of different databases for all created meta files
        containing information about plates, filenames, siRNAs, genes, etc.

        :param path: the path where the parsed files are placed
        """

        # creates meta file database and one file for every plate
        # and feature type
        self._create_dbs()
        # reads file names ending with meta.tsv into memory
        fls = list(
          filter(
            lambda x: x.endswith("_meta.tsv"), [f for f in os.listdir(path)]
          )
        )
        le = len(fls)
        # iterates over meta files and puts their info into the db
        for i, file in enumerate(fls):
            if i % 100 == 0:
                logger.info("Doing file {} of {}".format(i, le))
            self._insert(path, file)
        # puts indexes on all databases for fast file retrieval
        self._create_indexes()

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

    def _insert(self, path, file):
        filename = os.path.join(path, file)
        try:
            # statistics file name meta information
            ma = FILE_FEATURES_REGEX.match(file.replace("_meta.tsv", ""))
            stu, pat, lib, des, _, rep, pl, feature = ma.groups()
            # put the file classifier suffixes into the meta database
            # this really only regards the NAME of the file, the FEATURE it
            # is containing and the meta that describes the plate
            self._insert_file_suffixes_to_meta(
              filename, stu, pat, lib, des, rep, pl, feature)

            # read the meta file
            # and put the meta plate information (genes, sirnas) into the
            # database for the plate
            with open(filename, "r") as fh:
                meta = yaml.load(fh)
            self._insert_meta(filename, meta)

        except ValueError:
            logger.error("Could not match meta file {}".format(file))

    def _insert_file_suffixes_to_meta(self, file, study, bacteria, library,
                                      design, replicate, plate, featureclass):
        ins = self._create_into_meta_statement(
          file, study, bacteria, library, design,
          replicate, plate, featureclass
        )
        self.__connection.execute(ins)

    @staticmethod
    def _create_into_meta_statement(file, study, bacteria, library,
                                    design, replicate, plate, featureclass):
        return "INSERT INTO meta " \
               "({}, {}, {}, {}, {}, {}, {}, {}) " \
                   .format(STUDY,
                           PATHOGEN,
                           LIBRARY,
                           DESIGN,
                           REPLICATE,
                           PLATE,
                           FEATURECLASS,
                           "filename") + \
               "VALUES (" + \
               "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');" \
                   .format(study,
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
          file, meta, self._insert_into_statement)

    @staticmethod
    def _insert_into_statement(k, v, file):
        s = "INSERT INTO {} ({}, filename) VALUES('{}', '{}')" \
            .format(k, k, v, file)
        return s

    def _insert_features(self, file, meta):
        tab = self.feature_table_name(file)
        if not self._exists(tab):
            self._create_file_feature_table(tab)
            self.__connection.insert_many(meta, tab)

    @staticmethod
    def feature_table_name(file):
        return file.replace("_meta.tsv", "").split("/")[-1].replace("-", "_")

    def _exists(self, tab):
        ex = self.__connection.exists(tab)
        return ex

    def _create_file_feature_table(self, tab):
        s = "CREATE TABLE IF NOT EXISTS {}".format(tab) + \
            " (feature varchar(1000) NOT NULL, " + \
            "PRIMARY KEY(feature));"
        self.__connection.execute(s)

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
