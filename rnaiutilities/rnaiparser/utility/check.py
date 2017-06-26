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

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


def check_feature_group(fg):
    if not isinstance(fg, list):
        raise "Please provide a list"
    f1_cells = fg[0].ncells
    for j, f in enumerate(fg):
        fj_cells = f.ncells
        for i, fj_cells_i in enumerate(fj_cells):
            try:
                if f1_cells[i] != fj_cells_i:
                    logger.warning(
                      "Cell numbers between feature {} and feature {} differ: {} vs. {}".
                          format(fg[0].featurename,
                                 f.featurename,
                                 f1_cells[i],
                                 fj_cells_i))
            except IndexError:
                logger.warning("Cell array sizes differ: {} vs. {}".format(
                  fg[0].featurename, f.featurename))
