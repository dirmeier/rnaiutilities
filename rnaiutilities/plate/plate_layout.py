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

from rnaiutilities.plate.plate_well import PlateWell

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlateLayout(object):
    """
    Class for the sirna/gene layout for wells, i.e., the mapping of wells
     to sirnas/genes.
    """

    def __init__(self, classifier, geneset, library):
        """
        Constructor.

        :param classifier: the plate classifier
        :param geneset: ?
        :param library: ?
        """
        self._classifier = classifier
        self._geneset = geneset
        self._library = library
        self._well_layout = {}

    def add(self, gene, sirna, well, well_type):
        if well in self._well_layout:
            logger.warning("Adding " + well + " multiple times to " +
                        self._classifier + " layout!")
        self._well_layout[well] = PlateWell(gene, sirna, well, well_type)

    def sirna(self, well):
        if well not in self._well_layout:
            logger.warning("Could not find well:" + well)
            return None
        return self._well_layout[well].sirna

    def welltype(self, well):
        if well not in self._well_layout:
            logger.warning("Could not find well:" + well)
            return None
        return self._well_layout[well].welltype

    def gene(self, well):
        if well not in self._well_layout:
            logger.warning("Could not find well:" + well)
            return None
        return self._well_layout[well].gene
