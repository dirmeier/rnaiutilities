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
Module for various file related functions.
"""

import os
import logging
import numpy
from pathlib import Path
import scipy.io as spio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_base_filesnames(folder, suffix):
    """
    Get the basenames of all files fiven in `folder` that end with `suffix`.

    :param folder: the folder to look into
    :type folder: str
    :param suffix: the suffix files have to end with in order to be on the list
    :type suffix: str
    :return: list of file basenames
    """

    fls = []
    if not Path(folder).exists():
        logger.warning("{} does not exist.".format(folder))
    for _, _, f in os.walk(folder):
        for basename in f:
            if basename.endswith(suffix):
                fls.append(basename)
    return fls


def usable_feature_files(platefileset, usable_features):
    available_feature_files = _available_files(platefileset)
    fls = [
        data_filename(platefileset.outfile + "_" + x) for x in
        usable_features]
    uff = []
    for fl in fls:
        if any(fl.endswith("_" + av + "_data.tsv") for av in
               available_feature_files):
            uff.append(fl)
    return uff


def _available_files(platefileset):
    return numpy.unique(
      list(map(lambda x: x.split(".")[0],
               [x.featurename.lower() for x in platefileset.files])))


def data_filename(filename):
    return filename + "_data.tsv"


def meta_filename(filename):
    return filename + "_meta.tsv"


def load_matlab(file):
    """
    Load a matlab file as np array

    :param file: matlab file name
    :return: returns an numpy.array
    """
    matlab_matrix = spio.loadmat(file)
    return matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0]
