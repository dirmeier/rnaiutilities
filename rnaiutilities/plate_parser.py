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

import enforce
import numpy

from rnaiutilities.plate.plate_feature_matrix import FeatureMatrix
from rnaiutilities.plate.plate_file_set import PlateFileSet
from rnaiutilities.plate.plate_sirna_gene_mapping import PlateSirnaGeneMapping
from rnaiutilities.utility.files import load_matlab

logger = logging.getLogger(__name__)

__NA__ = "NA"


class PlateFilesParser:
    """
    Class for parsing single features files as numpy arrays.
    """

    @enforce.runtime_validation()
    def parse(self, pfs: PlateFileSet):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        Iterate over the file sets and create matrices every platefileset
        represents a plate so every platefileset is a single file.
        """

        features = self._parse_plate_file_set(pfs)
        mapping = self._parse_plate_mapping(pfs)
        return pfs, features, mapping

    def _parse_plate_file_set(self, pfs):
        logger.info(
          "Parsing plate file set to memory: {}".format(str(pfs.classifier)))
        features = {}
        for plate_file in pfs:
            try:
                cf = self._parse_file(plate_file)
                self._add(features, cf, cf.feature_group)
            except (
              ValueError, TypeError, AssertionError, FileNotFoundError) as e:
                logger.error(
                  "Could not parse: {} -> {}".format(plate_file, str(e)))
        if len(features) == 0:
            raise ValueError(
              "No files found for platefileset: {}".format(pfs.classifier))
        return features

    def _parse_file(self, plate_file):
        """
        Parse a matlab binary as np.array

        :param plate_file: the matlab file
        :return: returns a 2D np.array
        """

        featurename = plate_file.featurename
        file = plate_file.filename
        if file is None:
            raise FileNotFoundError("Could not find file: {}".format(file))
        matrix = self._alloc(load_matlab(file), file, featurename)
        return matrix

    @staticmethod
    def _alloc(arr, file, f_name):
        f_name = str(f_name).lower()
        if f_name.endswith(".mat"):
            f_name = f_name.replace(".mat", "")
        try:
            n_row = len(arr)
            row_lens = [len(x) for x in arr]
            max_n_col = max(row_lens)
            mat = numpy.full(shape=(n_row, max_n_col),
                             fill_value=numpy.Infinity,
                             dtype="float64")
            for i, _ in enumerate(arr):
                try:
                    row = arr[i]
                    mat[i][:len(row)] = row.flatten()
                except ValueError:
                    mat[i][0] = numpy.Infinity
            return FeatureMatrix(
              mat, n_row, max_n_col, file, row_lens, f_name)
        except AssertionError:
            raise AssertionError(
              "Could not alloc feature %s of %s", f_name, file)

    @staticmethod
    def _add(features, cf, feature_group):
        if feature_group not in features:
            features[feature_group] = []
        features[feature_group].append(cf)

    @staticmethod
    def _parse_plate_mapping(pfs):
        logger.info("Loading meta for plate file set: " + str(pfs.classifier))
        mapping = PlateSirnaGeneMapping(pfs)
        if len(mapping) == 0:
            raise ValueError(
              "Found no mapping for platefileset: {}".format(pfs.classifier))
        return mapping
