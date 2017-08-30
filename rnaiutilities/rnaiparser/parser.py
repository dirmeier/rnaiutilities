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
from pathlib import Path
import numpy as np
import multiprocessing as mp
from tabulate import tabulate

from rnaiutilities.rnaiparser.globals import USABLE_FEATURES
from rnaiutilities.rnaiparser.plate_list import PlateList
from rnaiutilities.rnaiparser.config import Config
from rnaiutilities.rnaiparser.plate_file_set_generator.plate_file_sets import \
    PlateFileSets
from rnaiutilities.rnaiparser.plate_layout import MetaLayout
from rnaiutilities.rnaiparser.plate_parser import PlateParser
from rnaiutilities.rnaiparser.plate_writer import PlateWriter
from rnaiutilities.rnaiparser.utility.io import get_base_filesnames
from rnaiutilities.rnaiparser.utility.math import jaccard

logger = mp.log_to_stderr()
logger.setLevel(logging.INFO)


class Parser:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    def __init__(self, config):
        """
        Constructor for PlateParser.

        :param config: a configuration for file parsing
        :type config: Config
        """
        if not isinstance(config, Config):
            raise ValueError("Please provide a config object")
        self._config = config
        self._output_path = config.output_path
        self._multi_processing = config.multi_processing
        # read the plate list files
        # oly take files with regex pooled/unpooled genome/kinome
        # TODO: this also needs to go to the config file
        # why is this again: (-\w+)* ?
        self._plate_list = PlateList(
          config.plate_id_file,
          ".*\/\w+\-\w[P|U]\-[G|K]\d+(-\w+)*\/.*"
        )
        # parse the folder into a map of (classifier-plate) pairs
        self._layout = MetaLayout(config.layout_file)
        self._parser = PlateParser()
        self._writer = PlateWriter(self._layout)

    def parse(self):
        """
        Parses the plate file sets into raw tsv files.

        """

        exps = list(self._plate_list.plate_files)
        # use globals vars for process pool
        if self._multi_processing:
            # number of cores we are using
            n_cores = mp.cpu_count() - 1
            logger.info("Going parallel with " + str(n_cores) + " cores!")
            pool = mp.Pool(processes=n_cores)
            _ = pool.map(func=self._parse, iterable=exps)
            pool.close()
            pool.join()
        else:
            for x in exps:
                self._parse(x)
        logger.info("All's well that ends well")

    def _parse(self, plate):
        try:
            platefilesets = self._filesets(
              self._output_path + "/" + plate,
              self._output_path
            )
            if len(platefilesets) > 1:
                logger.warning("Found multiple plate identifiers for: " + plate)
            ret = self._parse_plate_file_sets(platefilesets)
        except Exception as ex:
            logger.error("Found error parsing: " + str(plate) + ". " +
                         "Error:" + str(ex))
            ret = -1
        return ret

    @staticmethod
    def _filesets(folder, output_path):
        """
        Create a list of platefile sets contained in a folder. Recursively go
        through all the folders and add the found matlab files into the
        respective platefile set.

        :param folder: the folder that is recursively went through
        :param output_path: the output path where the platefile set is stored to
        :return: returns a platefilesets object
        """
        return PlateFileSets(folder, output_path)

    def _parse_plate_file_sets(self, platefilesets):
        if not isinstance(platefilesets, PlateFileSets):
            raise TypeError("no PlateFileSets object given")
        try:
            for platefileset in platefilesets:
                # create a list of relevant files for the plateset
                fls = self._usable_feature_files(platefileset)
                # if all the files exist, we just skip the creation of the files
                if any(not Path(x).exists() for x in fls):
                    logger.info("Doing: " + " ".join(platefileset.meta))
                    pfs, features, mapping = self._parser.parse(platefileset)
                    if pfs is not None:
                        self._writer.write(pfs, features, mapping)
                else:
                    logger.info(" ".join(map(str, platefileset.meta)) +
                                " already exists. Skipping.")
        except Exception as ex:
            logger.error("Some error idk anythin can happen here: " + str(ex))
        return 0

    def report(self):
        """
        Checks if all files have been parsed correctly.

        """

        for plate in self._plate_list:
            platefilesets = self._filesets(
              self._output_path + "/" + plate,
              self._output_path
            )
            if len(platefilesets) == 0:
                logger.warning("{} is missing entirely".format(plate))
            for platefileset in platefilesets:
                usable_feature_files = self._usable_feature_files(platefileset)
                cnt_all_files = len(usable_feature_files)
                cnt_avail_files = sum(
                  [Path(x).exists() for x in usable_feature_files])
                if cnt_all_files != cnt_avail_files:
                    logger.warning("{} has not been parsed completely -> only "
                                   "{}/{} files there.".format(
                      plate, cnt_avail_files, cnt_all_files))
        logger.info("All's well that ends well")

    @staticmethod
    def _available_files(platefileset):
        return np.unique(list(map(lambda x: x.split(".")[0],
                                  [x.featurename.lower() for x in
                                   platefileset.files])))

    def _usable_feature_files(self, platefileset):
        available_feature_files = self._available_files(platefileset)
        fls = [
            self._writer.data_filename(platefileset.outfile + "_" + x) for x in
            USABLE_FEATURES
        ]
        usable_feature_files = []
        for fl in fls:
            if any(fl.endswith("_" + av + "_data.tsv") for av in
                   available_feature_files):
                usable_feature_files.append(fl)
        return usable_feature_files

    def check_download(self):
        """
        Checks if all files given in config have been downloaded correctly.

        """

        logger.setLevel(logging.WARNING)
        for plate in self._plate_list:
            platefile_path = self._config.plate_folder + "/" + plate
            if not Path(platefile_path).exists():
                logger.warning("{} is missing".format(platefile_path))
            else:
                if self._has_correct_file_count(platefile_path):
                    logger.info(
                      "{} is available".format(platefile_path))
        logger.setLevel(logging.INFO)

    @staticmethod
    def _has_correct_file_count(platefile_path):
        for d, s, f in os.walk(platefile_path):
            if any(re.match("20\d+-\d+", el) for el in s):
                if len(s) > 1:
                    logger.warning(
                      "{} has multiple downloaded platefilesets".format(
                        platefile_path))
                    return False
            if len(s):
                continue
            files = list(filter(lambda x: x.endswith(".mat"), f))
            if len(files) == 0:
                logger.warning("{} has no files".format(platefile_path))
                return False
        return True

    def feature_sets(self):
        """
        Checks between all possible screens for pairwise feature overlaps.
        The overlaps can be taken to decide which screens to include in the analysis.

        """

        screen_map = self._screen_map()
        file_map = self._file_map(screen_map)
        keys = sorted(list(file_map.keys()))
        tab = []
        for i in range(len(keys)):
            row = [keys[i]]
            for j in range(len(keys)):
                if j > i:
                    row.append("{:2.5f}".format(jaccard(file_map[keys[i]], file_map[keys[j]])))
                else:
                    row.append(str(0))
            tab.append(row)
        print(tabulate(tab, headers = [""] + keys ))

    def _screen_map(self):
        """
        Computes a mapping screen -> plate, i.e. sth like:
        BRUCELLA-DP-K2 -> {plate1, plate2, plate }

        :return: returns a mapping
        :rtype: dict(str, str)
        """
        screen_map = {}
        for plate in self._plate_list:
            platefile_path = self._config.plate_folder + "/" + plate
            screen = self._to_screen(plate)
            if screen not in screen_map:
                screen_map[screen] = set()
            screen_map[screen].add(platefile_path)
        return screen_map

    @staticmethod
    def _to_screen(plate):
        """
        Parses sth like this: "/(GROUP_COSSART)/LISTERIA_TEAM/(LISTERIA-DP-G)1/DZ44-1K"

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
            self._check_file_counts(file_count_map, size)
            file_map[screen] = list(file_count_map.keys())
        return file_map

    @staticmethod
    def _get_suffixes(fileset):
        return get_base_filesnames(fileset, ".mat")

    def _get_screen_file_map(self, platesets):
        file_map = {}
        for plateset in platesets:
            # list of files ending in *mat
            feature_list = self._get_suffixes(plateset)
            for fl_suffix in feature_list:
                if fl_suffix not in file_map:
                    file_map[fl_suffix] = 0
                # increment the number of times a feature has been found
                file_map[fl_suffix] += 1
        return file_map

    @staticmethod
    def _check_file_counts(file_map, size):
        for fl_suffix in file_map:
            if file_map[fl_suffix] != size:
                logger.warning(
                  "Plate-set {} does not have {} files each."
                      .format(fl_suffix, size))
