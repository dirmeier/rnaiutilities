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
    Tests the control querying module for data base querying.
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        folder = os.path.join(os.path.dirname(__file__), "..", "data")
        db_folder = os.path.join(folder, "out")
        db_file = os.path.join(db_folder, "database.db")
        self._query = Query(db_file)

    def test_query_size(self):
        res = self._query.query()
        assert len(res) == 3

    def test_query_featureclass(self):
        assert len(self._query.query(featureclass="cells")) == 1
        assert len(self._query.query(featureclass="nuclei")) == 1
        assert len(self._query.query(featureclass="perinuclei")) == 1

    def test_query_wrong_featureclass(self):
        with pytest.raises(SystemExit):
            _ = self._query.query(featureclass="hallo")

    def test_query_elements(self):
        q = self._query.query(
          featureclass="cells", study="study", pathogen="bacteria",
          library="d", design="p", plate="kb03-1a")
        assert list(q[0][1:-1]) == \
               ["study", "bacteria", "d", "p", "1", "kb03-1a", "cells"]

    def test_compose(self):
        res = self._query.compose()
        res.dump(sample=10, normalize="zscore",
                 fh="/Users/simondi/Desktop/data.tsv")
        assert 1 == 1
