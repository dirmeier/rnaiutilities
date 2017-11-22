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
import pandas
import unittest
import shutil

import pytest

from rnaiutilities import Parser, Config
from rnaiutilities.utility.files import read_yaml

logging.basicConfig(level=logging.DEBUG)


class TestParser(unittest.TestCase):
    """
    Tests the control parsing module.

    """

    files = [
        "study-bacteria-d-p-k-1-kb03-1a_nuclei_data.tsv",
        "study-bacteria-d-p-k-1-kb03-1a_cells_data.tsv",
        "study-bacteria-d-p-k-1-kb03-1a_perinuclei_data.tsv"]
    meta = [
        "study-bacteria-d-p-k-1-kb03-1a_nuclei_meta.tsv",
        "study-bacteria-d-p-k-1-kb03-1a_cells_meta.tsv",
        "study-bacteria-d-p-k-1-kb03-1a_perinuclei_meta.tsv"]

    @classmethod
    def setUpClass(cls):
        folder = os.path.join(os.path.dirname(__file__), "..", "data")
        TestParser.exp_folder = os.path.join(folder, "out")
        file = os.path.join(folder, "config.yml")

        conf = Config(file)
        conf._plate_id_file = os.path.join(folder, "experiment_meta_file.tsv")
        conf._plate_regex = ".*\/\w+\-\w[P|U]\-[G|K]\d+(-\w+)*\/.*"
        conf._layout_file = os.path.join(folder, "layout.tsv")
        conf._plate_folder = folder
        conf._output_path = os.path.join(folder, "out", "test_files")
        conf._multiprocessing = False

        TestParser.layoutfile = os.path.join(TestParser.exp_folder,
                                             "layout.tsv")
        TestParser.outfolder = conf._output_path
        if os.path.exists(TestParser.outfolder):
            shutil.rmtree(TestParser.outfolder)
        os.makedirs(TestParser.outfolder)

        parser = Parser(conf)
        parser.parse()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestParser.outfolder)

    def test_file_count(self):
        test_files = glob.glob1(TestParser.outfolder, ".tsv")
        expected_files = glob.glob1(TestParser.exp_folder, ".tsv")
        assert len(test_files) == len(expected_files)

    def test_data_file_equality(self):
        for f in TestParser.files:
            exp_data = pandas.read_csv(
              os.path.join(TestParser.exp_folder, f), sep="\t", header=0)
            parsed_data = pandas.read_csv(
              os.path.join(TestParser.outfolder, f), sep="\t", header=0)
            assert exp_data.equals(parsed_data)

    def test_meta_file_equality(self):
        for f in TestParser.meta:
            exp_data = read_yaml(os.path.join(TestParser.exp_folder, f))
            parsed_data = read_yaml(os.path.join(TestParser.outfolder, f))
            assert \
                sorted(exp_data["elements"]) == sorted(parsed_data["elements"])
            assert exp_data["features"] == parsed_data["features"]

    def test_cell_data_file_values(self):
        parsed_data = pandas.read_csv(os.path.join(
          TestParser.outfolder,
          "study-bacteria-d-p-k-1-kb03-1a_cells_data.tsv"),
          sep="\t", header=0)
        exp_col = "cells.intensity_maxintensityedge_corr1actin"
        # these values are manually looked up, so you need to have a look in
        # the respective matlab files
        assert exp_col in parsed_data.columns
        assert parsed_data[exp_col].values[1 - 1] == pytest.approx(0.1714, 0.01)
        assert parsed_data[exp_col].values[192 - 1 + 1] == pytest.approx(0.0612,
                                                                         0.01)
        assert parsed_data[exp_col].values[-1] == pytest.approx(0.0699, 0.01)

    def test_nuclei_data_file_values(self):
        parsed_data = pandas.read_csv(os.path.join(
          TestParser.outfolder,
          "study-bacteria-d-p-k-1-kb03-1a_nuclei_data.tsv"),
          sep="\t", header=0)
        exp_col = "nuclei.intensity_uppertenpercentintensity_corr1pathogen"
        # these values are manually looked up, so you need to have a look in
        # the respective matlab files
        assert exp_col in parsed_data.columns
        assert parsed_data[exp_col].values[1 - 1] == pytest.approx(0.0526,
                                                                   0.01)
        assert parsed_data[exp_col].values[192 - 1 + 1] == pytest.approx(0.0120,
                                                                         0.01)
        assert parsed_data[exp_col].values[-1] == pytest.approx(0.0128, 0.01)

    def test_perinuclei_data_file_values(self):
        parsed_data = pandas.read_csv(os.path.join(
          TestParser.outfolder,
          "study-bacteria-d-p-k-1-kb03-1a_perinuclei_data.tsv"),
          sep="\t", header=0)
        exp_col = "perinuclei.intensity_upperquartileintensity_corr1actin"
        # these values are manually looked up, so you need to have a look in
        # the respective matlab files
        assert exp_col in parsed_data.columns
        assert parsed_data[exp_col].values[1 - 1] == pytest.approx(0.1822,
                                                                   0.01)
        assert parsed_data[exp_col].values[192 - 1 + 1] == pytest.approx(0.0322,
                                                                         0.01)
        assert parsed_data[exp_col].values[-1] == pytest.approx(0.0287, 0.01)

    def test_perinuclei_data_file_values(self):
        parsed_data = pandas.read_csv(os.path.join(
          TestParser.outfolder,
          "study-bacteria-d-p-k-1-kb03-1a_perinuclei_data.tsv"),
          sep="\t", header=0)
        exp_col = "perinuclei.intensity_upperquartileintensity_corr1actin"
        # these values are manually looked up, so you need to have a look in
        # the respective matlab files
        assert exp_col in parsed_data.columns
        assert parsed_data[exp_col].values[1 - 1] == pytest.approx(
          0.1822, 0.01)
        assert parsed_data[exp_col].values[192 - 1 + 1] == pytest.approx(
          0.0322, 0.01)
        assert parsed_data[exp_col].values[-1] == pytest.approx(0.0287, 0.01)
