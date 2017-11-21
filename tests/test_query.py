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


class TestQuery(unittest.TestCase):
    """
    Tests the control querying module.

    """

    folder = os.path.join(os.path.dirname(__file__), "..", "data")
    db_folder = os.path.join(folder, "out", "test_db")
    db_file = os.path.join(db_folder, "database.db")
    path = os.path.join(folder, "out")

    @classmethod
    def setUpClass(cls):
        if os.path.exists(TestQuery.db_folder):
            shutil.rmtree(TestQuery.db_folder)
        os.makedirs(TestQuery.db_folder)

        Query(TestQuery.db_file).insert(TestQuery.path)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._conn = sqlite3.connect(TestQuery.db_file)

    def tearDown(self):
        self._conn.close()

    def test_insertion_creates_db(self):
        assert os.path.exists(TestQuery.db_file)

    def test_number_of_tables_created(self):
        c = self._conn.cursor()
        result = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        assert len(result) == 7

    def test_count_elemems_meta(self):
        c = self._conn.cursor()
        result = c.execute("SELECT * FROM meta;").fetchall()
        assert len(result) == 3

    def test_no_featurclass_raises_error(self):
        with pytest.raises(SystemExit):
            Query.compose(featureclass="test")
