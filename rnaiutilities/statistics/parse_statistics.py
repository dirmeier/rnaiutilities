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

from rnaiutilities.globals import USABLE_FEATURES
from rnaiutilities.plate.plate_file_set_generator import PlateFileSets
from rnaiutilities.utility.files import usable_feature_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ParseStatistics:
    """
    Class for checking if all files are parsed correctly.
    """

    def __init__(self, plate_list, plate_folder, output_path):
        """
        Constructor

        :param plate_list: the list of plates
        :type plate_list: list(str)
        :param plate_folder: the folder where all plates lie
        :type plate_folder: str
        :param output_path: the folder where all parsed files are put
        :type output_path: str
        """

        self._plate_list = plate_list
        self._plate_folder = plate_folder
        self._output_path = output_path

    def statistics(self):
        """
        Check if all files are parsed correctly.
        """

        for plate in self._plate_list:
            platefilesets = PlateFileSets(
              self._plate_folder + "/" + plate, self._output_path)
            if len(platefilesets) == 0:
                logger.warning("{} is missing entirely".format(plate))
            else:
                self._statistics(platefilesets, plate)
        logger.info("All's well that ends well")

    @staticmethod
    def _statistics(platefilesets, plate):
        for platefileset in platefilesets:
            uff = usable_feature_files(platefileset, USABLE_FEATURES)
            cnt_all_files = len(uff)
            cnt_avail_files = sum([Path(x).exists() for x in uff])
            if cnt_all_files != cnt_avail_files:
                logger.warning(
                  "{} has not been parsed completely -> only "
                  "{}/{} files there.".format(
                    plate, cnt_avail_files, cnt_all_files))
