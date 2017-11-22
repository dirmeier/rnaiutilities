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


import logging
import numpy
import os
import unittest
import pandas
import pytest
import shutil

from rnaiutilities import Query

logging.basicConfig(level=logging.DEBUG)


class TestQuery(unittest.TestCase):
    """
    Tests the control querying module for data base querying.
    """

    expected_feature_columns = [
        "cells.children_invasomes_count",
        "cells.intensity_maxintensityedge_corr1actin",
        "cells.parent_nuclei",
        "cells.children_bacteria_count",
        "nuclei.intensity_uppertenpercentintensity_corr1pathogen",
        "perinuclei.intensity_upperquartileintensity_corr1actin"]

    expected_columns = [
                           "study", "pathogen", "library", "design",
                           "replicate", "plate", "well", "gene", "sirna",
                           "well_type", "image_idx",
                           "object_idx"] + expected_feature_columns

    folder = os.path.join(os.path.dirname(__file__), "..", "data")
    db_folder = os.path.join(folder, "out")

    exp_file = os.path.join(db_folder, "data.tsv")
    out_folder = os.path.join(db_folder, "test_data")
    out_db_file = os.path.join(out_folder, "database.db")

    out_file_sampled = os.path.join(
      out_folder, "data_sampled.tsv")
    out_file_full = os.path.join(
      out_folder, "data_full.tsv")

    @classmethod
    def setUpClass(cls):
        if os.path.exists(TestQuery.out_folder):
            shutil.rmtree(TestQuery.out_folder)
        os.makedirs(TestQuery.out_folder)

        Query(TestQuery.out_db_file).insert(TestQuery.db_folder)

        TestQuery.res = Query(TestQuery.out_db_file).compose()
        numpy.random.seed(23)
        TestQuery.res.dump(sample=10, normalize="zscore",
                           fh=TestQuery.out_file_sampled)
        TestQuery.res.dump(sample=None, normalize="zscore",
                           fh=TestQuery.out_file_full)

        TestQuery.expected_data = pandas.read_csv(
          TestQuery.exp_file, sep='\t', header=0)
        TestQuery.composed_sampled_data = pandas.read_csv(
          TestQuery.out_file_sampled, sep='\t', header=0)
        TestQuery.composed_full_data = pandas.read_csv(
          TestQuery.out_file_full, sep='\t', header=0)

        ou = os.path.join(TestQuery.out_folder, "data_sampled_unnorm.tsv")
        numpy.random.seed(23)
        TestQuery.res.dump(sample=10, normalize=None, fh=ou)
        exf = os.path.join(TestQuery.db_folder, "data_unnormalized.tsv")
        TestQuery.ex_non_norm = pandas.read_csv(exf, sep='\t', header=0)
        TestQuery.composed_non_norm = pandas.read_csv(ou, sep='\t', header=0)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestQuery.out_folder)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._query = Query(TestQuery.out_db_file)

    def test_query_size(self):
        res = self._query.query()
        assert len(res) == 3

    def test_query_featureclass(self):
        assert len(self._query.query(featureclass="cells")) == 1
        assert len(self._query.query(featureclass="nuclei")) == 1
        assert len(self._query.query(featureclass="perinuclei")) == 1

    def test_query_wrong_featureclass(self):
        with pytest.raises(SystemExit):
            _ = self._query.query(featureclass="hallo")

    def test_query_elements(self):
        q = self._query.query(
          featureclass="cells", study="study", pathogen="bacteria",
          library="d", design="p", plate="kb03-1a")
        assert list(q[0][1:-1]) == \
               ["study", "bacteria", "d", "p", "1", "kb03-1a", "cells"]

    def test_compose_creates_correct_data(self):
        assert TestQuery.expected_data.equals(TestQuery.composed_sampled_data)

    def test_compose_creates_correct_non_norm_data(self):
        assert TestQuery.ex_non_norm.equals(TestQuery.composed_non_norm)

    def test_compose_creates_correct_non_norm_data_values(self):
        cell_col = TestQuery.composed_non_norm[
            "cells.intensity_maxintensityedge_corr1actin"]
        nuc_col = TestQuery.composed_non_norm[
            "nuclei.intensity_uppertenpercentintensity_corr1pathogen"]
        per_col = TestQuery.composed_non_norm[
            "perinuclei.intensity_upperquartileintensity_corr1actin"]
        assert cell_col.values[0] == pytest.approx(0.1628, 0.01)
        assert cell_col.values[6] == pytest.approx(0.206, 0.01)
        assert nuc_col.values[0] == pytest.approx(0.0145, 0.01)
        assert nuc_col.values[6] == pytest.approx(0.01498, 0.01)
        assert per_col.values[0] == pytest.approx(0.100, 0.01)
        assert per_col.values[6] == pytest.approx(0.066, 0.01)

    def test_compose_creates_correct_columns(self):
        for c in TestQuery.composed_sampled_data.columns:
            assert c in TestQuery.expected_columns

    def test_compose_creates_correct_well_counts(self):
        cnts = TestQuery.composed_sampled_data.groupby(
          ["gene", "sirna", "well"]).size().reset_index(name='counts')
        assert all(cnts["counts"] == 10)

    def test_compose_creates_zero_mean_columns(self):
        for c in TestQuery.expected_feature_columns:
            assert TestQuery.composed_full_data[c].mean() == \
                   pytest.approx(0, 0.01)

    def test_compose_creates_unit_variance_columns(self):
        for c in TestQuery.expected_feature_columns:
            st = TestQuery.composed_full_data[c].std()
            assert (st == pytest.approx(1, 0.01) or
                    st == pytest.approx(0, 0.01))

    def test_compose_creates_unit_variance_columns(self):
        for c in TestQuery.expected_feature_columns:
            st = TestQuery.composed_full_data[c].std()
            assert (st == pytest.approx(1, 0.01) or
                    st == pytest.approx(0, 0.01))
