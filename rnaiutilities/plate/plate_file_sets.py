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
import re

from rnaiutilities.globals import SKIPPABLE_FEATURE_NAMES, IMAGE_MAPPING_FILE, \
    IMAGE, SKIPPABLE_FEATURE_REGEX
from rnaiutilities.plate.plate_file import PlateFile
from rnaiutilities.plate.plate_file_set import PlateFileSet
from rnaiutilities.utility import regex
from rnaiutilities.utility.regex import parse_plate_info, parse_screen_details

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlateFileSets:
    """
    Class for keeping all the filenames of a plate with possible different
     timestamps or IDs stored as a map.
    """

    def __init__(self, folder, outfolder):
        self._setting_regex = re.compile("(\w+)(\d+)")
        self._folder = folder
        self._plate_file_sets = {}
        self._files = []
        self._outfolder = outfolder

        self._parse_plate_file_sets(folder)

    def __iter__(self):
        """
        Iterate over all the single plate filesets.
        """

        for _, v in self._plate_file_sets.items():
            yield v

    def __len__(self):
        return len(self._plate_file_sets)

    def _parse_plate_file_sets(self, folder):
        """
        Traverse the given folder structure and save every
        (classifier-folder) pair in a plate map.

        :param folder: the folder for which all the plates should get parsed
        """

        # iterate over the array of files
        for basename, filename in self._find_files(folder):
            self._files.append(filename)
            if self._skip(basename):
                continue
            self._parse_file_name(filename)

    def _parse_file_name(self, filename):
        clss, st, pa, lib, des, scr, rep, suf, plate, feature \
            = self._parse_plate_name(filename)

        self._add_platefileset(
          clss, st, pa, lib, des, scr, rep, suf, plate, self._outfolder)
        self._add_platefile(filename, feature, clss)

    def _skip(self, basename):
        b = basename.lower()
        if self._skip_feature(b):
            return True
        if b.startswith(IMAGE) and \
           not b.startswith(IMAGE_MAPPING_FILE):
            return True
        return False

    def _add_platefile(self, f, feature, classifier):
        # matlab file is the well mapping
        if feature.lower() == IMAGE_MAPPING_FILE:
            self._plate_file_sets[classifier].mapping = PlateFile(f, feature)
        # add the current matlab file do the respective platefile
        else:
            self._plate_file_sets[classifier].files.append(
                PlateFile(f, feature))

    @staticmethod
    def _find_files(folder):
        """
        Traverse the folder and return all relevant matlab files

        :param folder: the folder for which all the plates should get parsed
        :return: returns a list of matlab files
        """
        for d, _, f in os.walk(folder):
            for basename in f:
                if basename.endswith(".mat"):
                    yield basename, os.path.join(d, basename)

    @staticmethod
    def _skip_feature(basename):
        b = basename.lower()
        for skip in SKIPPABLE_FEATURE_NAMES:
            if b.startswith(skip):
                return True
        for skip in SKIPPABLE_FEATURE_REGEX:
            if skip.match(b):
                return True
        return False

    @staticmethod
    def _parse_plate_name(f):
        """
        Decompose a filename into several features names.

        :param f: the file name
        :return: returns a list of feature names
        """
        screen, plate = parse_plate_info(f.strip().lower())
        st, pa, lib, des, scr, rep, suf = parse_screen_details(screen)
        feature = (f.split("/")[-1]).replace(".mat", "")
        if suf != regex.__NA__:
            classifier = "-".join([st, pa, lib, des, scr, rep, suf, plate])
        else:
            classifier = "-".join([st, pa, lib, des, scr, rep, plate])
        return classifier, st, pa, lib, des, scr, rep, suf, plate, feature

    def _add_platefileset(self, classifier, study, pathogen, library, design,
                          screen, replicate, suffix, plate, outfolder):
        if classifier not in self._plate_file_sets:
            self._plate_file_sets[classifier] = \
                PlateFileSet(classifier, outfolder + '/' + classifier,
                             study, pathogen, library, design,
                             screen, replicate, suffix, plate)
