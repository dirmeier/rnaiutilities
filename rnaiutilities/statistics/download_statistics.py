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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DownloadStatistics:
    """
    Class for checking if all files are available readily.
    """
    def __init__(self, plate_list, plate_folder):
        """
        Constructor

        :param plate_list: the list of plates
        :type plate_list: list(str)
        :param plate_folder: the folder where all plates lie
        :type plate_folder: str
        """

        self._plate_list = plate_list
        self._plate_folder = plate_folder

    def statistics(self):
        """
        Check if all files are available readily and compute some numbers.
        """

        logger.setLevel(logging.DEBUG)
        for plate in self._plate_list:
            platefile_path = self._plate_folder + "/" + plate
            if not Path(platefile_path).exists():
                logger.warning("{} is missing".format(platefile_path))
            else:
                if self._has_correct_file_count(platefile_path):
                    logger.info("{} is available".format(platefile_path))
        logger.setLevel(logging.INFO)

    @staticmethod
    def _has_correct_file_count(platefile_path):
        for _, s, f in os.walk(platefile_path):
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
