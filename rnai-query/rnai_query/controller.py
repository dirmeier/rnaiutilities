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

from rnai_query.filesets import table_file_sets
from rnai_query.result_set import ResultSet

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

logger = logging.getLogger(__name__)


class Controller:

    def __init__(self, db=None):
        # filesets of meta files
        self._table = table_file_sets.TableFileSets(db)

    def query(self, **kwargs):
        """
        Get a lazy file result set from some filtering criteria and a fixed 
        sample size.
                
        :param kwargs: the filtering criteria. 
        :return: returns a lazy ResultSet
        :rtype: ResultSet
        """
        fls = self._table.filter(**kwargs)
        return ResultSet(fls, **kwargs)
