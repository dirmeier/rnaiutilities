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
# @email = 'simon.dirmeier@bssae.ethz.ch'


import glob
import logging
import os
import unittest
import shutil

from rnaiutilities import Parser, Config

logging.basicConfig(level=logging.DEBUG)


class TestParser(unittest.TestCase):
    """
    Tests the control parsing module.

    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self._testfolder = os.path.join(self._folder, "out")
        self._file = os.path.join(self._folder, "config.yml")

        conf = Config(self._file)
        conf._plate_id_file = os.path.join(
          self._folder, "experiment_meta_file.tsv")
        conf._plate_regex = ".*\/\w+\-\w[P|U]\-[G|K]\d+(-\w+)*\/.*"
        conf._layout_file = os.path.join(self._folder, "layout.tsv")
        conf._plate_folder = self._folder
        conf._output_path = os.path.join(self._folder, "out", "test_files")
        conf._multiprocessing = False

        self._outfolder = conf._output_path
        if os.path.exists(self._outfolder):
            shutil.rmtree(self._outfolder)
        os.makedirs(self._outfolder)

        self._parser = Parser(conf)
        self._parser.parse()

    def test_file_count(self):
        test_files = glob.glob1(self._testfolder, ".tsv")
        expected_files = glob.glob1(self._outfolder, ".tsv")
        assert len(test_files) == len(expected_files)
