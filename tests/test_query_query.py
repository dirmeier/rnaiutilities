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
# @email = 'simon.dirmeier@bssae.ethz.ch'


import logging
import os
import unittest
import shutil
import sqlite3

import pytest

from rnaiutilities import Query

logging.basicConfig(level=logging.DEBUG)


class TestQueryInsert(unittest.TestCase):
    """
    Tests the control querying module.

    """

    folder = os.path.join(os.path.dirname(__file__), "..", "data")
    db_folder = os.path.join(folder, "out", "test_db")
    db_file = os.path.join(db_folder, "database.db")
    path = os.path.join(folder, "out")

    @classmethod
    def setUpClass(cls):
        if os.path.exists(TestQueryInsert.db_folder):
            shutil.rmtree(TestQueryInsert.db_folder)
        os.makedirs(TestQueryInsert.db_folder)

        Query(TestQueryInsert.db_file).insert(TestQueryInsert.path)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._conn = sqlite3.connect(TestQueryInsert.db_file)

    def tearDown(self):
        self._conn.close()

    def test_insertion_creates_db(self):
        assert os.path.exists(TestQueryInsert.db_file)

    def test_number_of_tables_created(self):
        c = self._conn.cursor()
        result = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        assert len(result) == 7

    def test_table_names(self):
        c = self._conn.cursor()
        result = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        expected_names = ["gene", "sirna", "well", "meta",
                          "study_bacteria_d_p_k_1_kb03_1a_cells",
                          "study_bacteria_d_p_k_1_kb03_1a_nuclei",
                          "study_bacteria_d_p_k_1_kb03_1a_perinucleo"]
        for x in result:
            assert x[0] in expected_names

    def test_number_of_meta_elements(self):
        c = self._conn.cursor()
        result = c.execute("SELECT * FROM meta;").fetchall()
        assert len(result) == 3

    def test_number_of_gene_elements(self):
        c = self._conn.cursor()
        result = c.execute("SELECT * FROM gene;").fetchall()
        assert len(result) == 3 * 384

    def test_number_of_sirna_elements(self):
        c = self._conn.cursor()
        result = c.execute("SELECT * FROM sirna;").fetchall()
        assert len(result) == 3 * 384

    def test_number_of_sirna_elements(self):
        c = self._conn.cursor()
        result = c.execute("SELECT * FROM sirna;").fetchall()
        assert len(result) == 3 * 384

    def test_no_featurclass_raises_error(self):
        with pytest.raises(SystemExit):
            Query.compose(featureclass="test")