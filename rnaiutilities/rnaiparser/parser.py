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
from pathlib import Path

import multiprocessing as mp

from rnaiutilities.rnaiparser.globals import USABLE_FEATURES
from rnaiutilities.rnaiparser.plate_list import PlateList
from rnaiutilities.rnaiparser.config import Config
from rnaiutilities.rnaiparser.plate_file_set_generator.plate_file_sets import PlateFileSets
from rnaiutilities.rnaiparser.plate_layout import MetaLayout
from rnaiutilities.rnaiparser.plate_parser import PlateParser
from rnaiutilities.rnaiparser.plate_writer import PlateWriter


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
        Iterate over the experiments, download the files, parse them and
        store to data-base.

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
                fls = [
                    self._writer.data_filename(platefileset.outfile + "_" + x)
                    for x in USABLE_FEATURES
                ]
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
        for plate in self._plate_list:
            platefilesets = self._filesets(
              self._output_path + "/" + plate,
              self._output_path
            )
            if len(platefilesets) == 0:
                print("{} is missing entirely".format(plate))
            for platefileset in platefilesets:
                fls = [
                    self._writer.data_filename(platefileset.outfile + "_" + x)
                    for x in USABLE_FEATURES
                ]
                cnt_all_files = len(fls)
                cnt_avail_files = sum([Path(x).exists() for x in fls])
                # if cnt_all_files != cnt_avail_files:
                print(
                    "{} has not been parsed completely -> only "
                    "{}/{} files there.".format(
                        plate, cnt_avail_files, cnt_all_files))

        logger.info("All's well that ends well")

    def check_download(self):
        logger.setLevel(logging.WARNING)
        for plate in self._plate_list:
            platefile_path = self._config.plate_folder + "/" + plate
            if not Path(platefile_path).exists():
                logger.warning("{} is missing".format(platefile_path))
            else:
                logger.info("{} is available".format(platefile_path))
        logger.setLevel(logging.INFO)
