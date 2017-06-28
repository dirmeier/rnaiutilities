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


import yaml
import logging

logging.basicConfig(
  level=logging.WARNING,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class Config:
    __PLATE_ID_FILE__ = "plate_id_file"
    __LAYOUT_FILE__ = "layout_file"
    __PLATE_FOLDER__ = "plate_folder"
    __OUTPUT_PATH__ = "output_path"
    __MULTI_PROCESSING__ = "multiprocessing"
    __CONFIG__ = \
        [
            __PLATE_FOLDER__, __PLATE_ID_FILE__, __LAYOUT_FILE__,
            __MULTI_PROCESSING__, __OUTPUT_PATH__
        ]

    def __init__(self, credentials):
        with open(credentials, 'r') as f:
            doc = yaml.load(f)
            for credential in Config.__CONFIG__:
                if credential not in doc:
                    logger.error(
                        "Could not find credential: " + str(credential))
                    exit(-1)
                setattr(self, "_" + credential, doc[credential])

    @property
    def plate_id_file(self):
        return getattr(self, "_" + Config.__PLATE_ID_FILE__)

    @property
    def layout_file(self):
        return getattr(self, "_" + Config.__LAYOUT_FILE__)

    @property
    def multi_processing(self):
        return bool(getattr(self, "_" + Config.__MULTI_PROCESSING__))

    @property
    def output_path(self):
        return getattr(self, "_" + Config.__OUTPUT_PATH__) + "/"

    @property
    def plate_folder(self):
        return getattr(self, "_" + Config.__PLATE_FOLDER__)
