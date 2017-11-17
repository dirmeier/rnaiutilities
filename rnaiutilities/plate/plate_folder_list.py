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

from rnaiutilities.globals import UNUSED_PLATE_FEATURE_REGEX

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlateFolderList:
    """
    Class that stores plate folder names in an array and filters plates that
    are not needed or wanted.

    """

    def __init__(self, file, pattern):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        :param pattern: a regex that you want to use for file searching
        """
        self._meta_file = file
        self._pattern = pattern
        logger.info("Loading experiments...")
        self._plate_folders = self._load()

    def __iter__(self):
        for f in self._plate_folders:
            yield f

    @property
    def folders(self):
        return self._plate_folders

    def _load(self):
        fls = []
        pat = re.compile(self._pattern)
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                entry = entry.upper()
                if entry.startswith("PLATENAME"):
                    continue
                toks = entry.strip().split("\t")
                if len(toks) < 2:
                    continue
                filename, platetype = toks[0], toks[1]
                if not (platetype.lower().startswith("screeningplate") or
                            platetype.lower().startswith("checkerboard") or
                            platetype.lower().startswith("mockplate")):
                    continue
                if UNUSED_PLATE_FEATURE_REGEX.match(filename) \
                   or not pat.match(filename):
                    continue
                fls.append(filename)
        return fls
