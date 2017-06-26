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


from numpy import shape


class PlateCellFeature:
    """
    Class that stores the features for a single matlab files

    """

    def __init__(self, mat, n_images, n_max_cells_count,
                 filename, n_cells_per_image,
                 featurename):
        """
        :param mat: the parsed matrix
        :param n_images: the number of images * wells (this usually is 3456).
        :param n_max_cells_count: the max number of cells on the well
        :param filename: name of the feature file
        :param n_cells_per_image: the number of cells per image

        """
        self._mat = mat
        self._n_images = n_images
        self._n_max_cells_count = n_max_cells_count
        self._filename = filename
        self._n_cells_per_image = n_cells_per_image
        self._featurename = featurename.lower()
        self._feature_group, self._short_feature_name = self._featurename.split(".")[0:2]
        assert (shape(self._mat)[0] == self._n_images)
        assert (shape(self._mat)[1] == self._n_max_cells_count)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Feature " + self._featurename

    @property
    def max_cells(self):
        return self._n_max_cells_count

    @property
    def values(self):
        return self._mat

    @property
    def featurename(self):
        return self._featurename

    @property
    def ncells(self):
        return self._n_cells_per_image

    @property
    def feature_group(self):
        return self._feature_group

    @property
    def short_name(self):
        return self._short_feature_name