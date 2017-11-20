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


def filter_by_prefix(arr, prefixes):
    """
    Filter the values of an array by a list of suffixes. Only the elements are
    returned that have a prefix found in the list of prefixes

    :param arr: the array to filter
    :param prefixes: a list of prefixes to filter from
    :return: returns a sublist of arr
    """

    els = filter(lambda x: any(x.startswith(p) for p in prefixes), arr)
    return list(els)


def inverse_filter_by_prefix(arr, prefixes):
    """
    Filter the values of an array by a list of suffixes. Only the elements are
    returned that have a prefix found in the list of prefixes

    :param arr: the array to filter
    :param prefixes: a list of prefixes to filter from
    :return: returns a sublist of arr
    """
    els = filter(lambda x: not any(x.startswith(f) for f in prefixes), arr)
    return list(els)
