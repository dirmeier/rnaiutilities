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


import re
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

__screen_regex__ = re.compile("^(\S+-?\S+)-(\w+)-(\w)(\w)-(\w+)(\d+)(-(.*))?$")
__screen_plate_regex__ = re.compile(".*/(.*)/.*/(.*)/(.*)/.*/.*/.+mat?$")
__NA__ = "NA"


def parse_screen_details(screen):
    """
    Parse a screen into an array of substrings, each being a detail of the
    screen:
    study, pathogen,
    library,
    design, screen, replicate, suffix

    :param screen: a screen string, such as "GROUP_COSSART-LISTERIA-DP-G1" or "GROUP_COSSART-LISTERIA-DP-G1-SUFFIX"
    :return: returns an array of details
    """
    try:
        pat = __screen_regex__.match(screen.lower())
        if pat is None:
            return [None] * 7
        return pat.group(1), pat.group(2), pat.group(3), pat.group(4), \
               pat.group(5), pat.group(6), \
               pat.group(8) if pat.group(8) is not None else __NA__
    except AttributeError:
        logger.warn("Could not parse: " + str(screen))
        return None


def parse_plate_info(mat_file):
    """
    Takes the absolut path of a matlab file and parses the screen name and

    the plate name from it
    :param mat_file: the absolute filename of a matlab file
    :return: returns an array of screenname and plate name
    """
    ret = __screen_plate_regex__.match(mat_file)
    return ret.group(1) + "-" + ret.group(2), ret.group(3)
