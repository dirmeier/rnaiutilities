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


from numpy import intersect1d, union1d


def jaccard(s, t):
    """
    Computes the Jaccard index between two lists.

    :param s: list(str)
    :param t: list(str)
    :return: returns the Jaccard index between the two sets
    :rtype: float
    """

    try:
        intr =  len(intersect1d(s, t)) / len(union1d(s, t))
    except ZeroDivisionError:
        intr  = 0
    return  intr
