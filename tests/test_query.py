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

from rnaiutilities import Query

logging.basicConfig(level=logging.DEBUG)


class TestQuery(unittest.TestCase):
    """
    Tests the control querying module.

    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self._db_folder = os.path.join(self._folder, "out", "test_files")
        self._db_file = os.path.join(self._db_folder, "database.db")
        self._path = os.path.join(self._folder, "out")

        if os.path.exists(self._db_folder):
            shutil.rmtree(self._db_folder)
        os.makedirs(self._db_folder)

        self._query = Query(self._db_file)
        self._query.insert(self._path)

    def test_insertion_creates_db(self):
        assert os.path.exists(self._db_file)
