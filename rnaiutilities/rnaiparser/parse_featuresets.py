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


import re
import logging
from tabulate import tabulate

from rnaiutilities.rnaiparser.utility.math import jaccard

from rnaiutilities.rnaiparser.utility.io import get_base_filesnames

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FeatureSetParser:
    def __init__(self, plate_list, plate_folder, outfile):
        self._plate_list = plate_list
        self._plate_folder = plate_folder
        self._outfile = outfile

    def parse(self):
        self._parse()

    def _parse(self):
        jaccard_file, feature_file = self._get_feature_set_files(self._outfile)
        f_map = self._file_map(self._screen_map())
        self._write(jaccard_file, feature_file,
                    sorted(list(f_map.keys())), f_map)

    @staticmethod
    def _write(jaccard_file, feature_file, keys, f_map):
        tab = []
        with open(feature_file, "w") as ff:
            for i, _ in enumerate(keys):
                row = [keys[i]]
                ff.write("#" + keys[i] + "\t" + ",".join(f_map[keys[i]]) + "\n")
                for j, _ in enumerate(keys):
                    sim = jaccard(f_map[keys[i]], f_map[keys[j]])
                    row.append("{:2.5f}".format(sim))
                tab.append(row)
                tab.append(row)
        with open(jaccard_file, "w") as jf:
            jf.write(tabulate(tab, headers=[""] + keys) + "\n")

    @staticmethod
    def _get_feature_set_files(file_name):
        reg = re.compile("(.*)(\..*)$").match(file_name)
        if reg is None:
            raise ValueError("Could not match filename")
        file_prefix, file_suffix = reg.group(1), reg.group(2)
        jaccard_file = file_prefix + "_jaccard" + file_suffix
        feature_file = file_prefix + "_feature_files" + file_suffix

        return jaccard_file, feature_file

    def _screen_map(self):
        screen_map = {}
        for plate in self._plate_list:
            platefile_path = self._plate_folder + "/" + plate
            screen = self._to_screen(plate)
            if screen not in screen_map:
                screen_map[screen] = set()
            screen_map[screen].add(platefile_path)
        return screen_map

    @staticmethod
    def _to_screen(plate):
        """
        Parses this: "/(GROUP_COSSART)/LISTERIA_TEAM/(LISTERIA-DP-G)1/DZ44-1K"
        """
        ma = re.match("^/(.+)/.+/(\w+-\w+-\w+)\d+.*/.+$", plate)
        return ma.group(1) + "-" + ma.group(2)

    def _file_map(self, screen_map):
        file_map = {}
        for screen, platesets in screen_map.items():
            # number of plate sets.
            # so every feature file should be found size times
            size = len(platesets)
            # maps a feat
            file_count_map = self._get_screen_file_map(platesets)
            self._check_file_counts(file_count_map, size, screen)
            file_map[screen] = list(file_count_map.keys())
        return file_map

    @staticmethod
    def _get_screen_file_map(platesets):
        file_map = {}
        for plateset in platesets:
            # list of files ending in *mat
            feature_list = get_base_filesnames(plateset, ".mat")
            for fl_suffix in feature_list:
                if fl_suffix not in file_map:
                    file_map[fl_suffix] = 0
                # increment the number of times a feature has been found
                file_map[fl_suffix] += 1
        return file_map

    @staticmethod
    def _check_file_counts(file_map, size, screen):
        for fl_suffix in file_map:
            if file_map[fl_suffix] != size:
                logger.warning(
                  "Screen {} has only {}/{} files for feature {}."
                      .format(screen, file_map[fl_suffix], size, fl_suffix))
