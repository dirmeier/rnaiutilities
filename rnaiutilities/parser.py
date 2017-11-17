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

"""
Main module (entry point) for parsing feature files.
"""

import logging
import multiprocessing as mp
from pathlib import Path

from rnaiutilities.config import Config
from rnaiutilities.globals import USABLE_FEATURES
from rnaiutilities.plate.layout import MetaLayout
from rnaiutilities.plate.plate_file_sets import \
    PlateFileSets
from rnaiutilities.plate.plate_list import PlateList
from rnaiutilities.plate_parser import PlateParser
from rnaiutilities.plate_writer import PlateWriter
from rnaiutilities.statistics.download_statistics import DownloadStatistics
from rnaiutilities.statistics.featureset_statistics import FeatureSetStatistics
from rnaiutilities.statistics.parse_statistics import ParseStatistics
from rnaiutilities.utility.files import usable_feature_files

logger = mp.log_to_stderr()
logger.setLevel(logging.INFO)


class Parser:
    """
    Class for parsing a folder of plates containing matlab files for the
    features.
    """

    def __init__(self, config):
        """
        Constructor for Parser.

        :param config: a configuration for file parsing
        :type config: Config
        """
        if not isinstance(config, Config):
            raise ValueError("Please provide a config object")
        self._config = config
        self._plate_folder = config.plate_folder
        self._output_path = config.output_path
        self._multi_processing = config.multi_processing
        # read the plate list files
        # only take files with regex pooled/unpooled genome/kinome
        # TODO: this also needs to go to the config file
        self._plate_list = PlateList(
          config.plate_id_file,
          ".*\/\w+\-\w[P|U]\-[G|K]\d+(-\w+)*\/.*")
        # statistics the folder into a map of (classifier-plate) pairs
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
            platefilesets = PlateFileSets(self._output_path + "/" + plate,
                                          self._output_path)
            if len(platefilesets) > 1:
                logger.warning("Found multiple plate identifiers for: " + plate)
            ret = self._parse_plate_file_sets(platefilesets)
        except Exception as ex:
            logger.error("Found error parsing: " + str(plate) + ". " +
                         "Error:" + str(ex))
            ret = -1
        return ret

    def _parse_plate_file_sets(self, platefilesets):
        if not isinstance(platefilesets, PlateFileSets):
            raise TypeError("no PlateFileSets object given")
        try:
            for platefileset in platefilesets:
                self._parse_plate_file_set(platefileset)
        except Exception as ex:
            logger.error("Some error idk anything can happen here: " + str(ex))
        return 0

    def _parse_plate_file_set(self, platefileset):
        # create a list of relevant files for the plateset
        fls = usable_feature_files(platefileset, USABLE_FEATURES)
        # if all the files exist, we just skip the creation of the files
        if any(not Path(x).exists() for x in fls):
            logger.info("Doing: " + " ".join(platefileset.meta))
            pfs, features, mapping = self._parser.parse(platefileset)
            if pfs is not None:
                self._writer.write(pfs, features, mapping)
        else:
            logger.info(" ".join(map(str, platefileset.meta)) +
                        " already exists. Skipping.")

    def parse_statistics(self):
        """
        Computes parsing statistics.

        """
        ParseStatistics(
          self._plate_list, self._plate_folder, self._output_path).statistics()

    def download_statistics(self):
        """
        Computes download statistics if all files given in config have been
        downloaded correctly.
        """
        DownloadStatistics(self._plate_list, self._plate_folder).statistics()

    def featureset_statistics(self, outfile):
        """
        Computes statistics between all possible screens for pairwise feature
         overlaps. The overlaps can be taken to decide which screens to include.
        """

        FeatureSetStatistics(
          self._plate_list, self._plate_folder, outfile).statistics()
