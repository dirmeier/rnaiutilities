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
import re

from rnaiutilities.utility import load_matlab

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlateSirnaGeneMapping:
    """
    Class that stores plate sirna-gene mappings.

    """

    def __init__(self, plate_file_set):
        if plate_file_set.mapping is not None:
            self._mapping = []
            self._pattern = re.compile(".*\_w(\\w\\d+)\_s\d\_z\d.*")
            self._load(plate_file_set)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._mapping[item]
        return None

    def __len__(self):
        return len(self._mapping)

    def _load(self, plate_file_set):
        """
        Load the sirna-gene mapping file

        :param plate_file_set: plate file set object
        """
        mlfile = load_matlab(plate_file_set.mapping.filename)
        if mlfile is None:
            return
        # create mapping array of same length
        self._mapping = [None] * len(mlfile)
        # pattern for every line: we are instested in a char, followed by 2
        # numbers
        for i, e in enumerate(mlfile):
            self._load_entry(i, self._pattern.match(e[0]))

    def _load_entry(self, i, mat):
        """
        Load a single line/image from the well mapping

        """

        if mat is None:
            return
        self._mapping[i] = mat.group(1).lower()
