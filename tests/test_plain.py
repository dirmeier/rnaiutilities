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


import unittest
import pytest
from rnaiutilities import Query


class TestPlain(unittest.TestCase):
    """
    Little fake test to make travis happy

    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._q = Query()

    def test_no_featurclass_raises_error(self):
        with pytest.raises(SystemExit):
            self._q.compose(featureclass="test")
