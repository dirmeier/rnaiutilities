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

from rnaiutilities.db.dbms import DBMS
from rnaiutilities.filesets import table_file_sets
from rnaiutilities.query_result_set import ResultSet

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Query:
    # TODO: put this to another place
    __selectable_features__ = ["cells", "perinuclei", "nuclei"]
    __filterable_features__ = ["study", "pathogen", "library",
                               "design", "gene", "sirna", "well",
                               "featureclass", "plate"]

    def __init__(self, db=None):
        """
        Create an instance to query a data.base

        :param db: if provided the filename of a sqlite database
        :type db: str
        """

        self._db = db
        # filesets of meta files
        self._table = table_file_sets.TableFileSets(db)

    def print(self,
              study=None,
              pathogen=None,
              library=None,
              design=None,
              replicate=None,
              plate=None,
              featureclass=None):
        """
        Query a database of image-based RNAi screening features for cells/bacteria/nuclei.
         The result will be printed to stdout.

        :param study: filters by study, e.g.
         'infectx'/'group_cossart'/'infectx_published'
        :param pathogen: filters by pathogen, e.g.
         'salmonella'/'adeno'/'bartonella'/'brucella'/'listeria'
        :param library: filters by library, e.g. 'a'/'d'/'q'
        :param design: filters by design, e.g.: 'p'/'u'
        :param replicate: filters by replicate, i.e. a number
        :param plate: filters by plate, i.e.: 'dz44-1l'
        :param featureclass: filters by featureclass,
         e.g. 'nuclei'/'cells'/'bacteria'
        """

        # TODO put this to another place
        if featureclass is not None:
            features = featureclass.split(",")
            for feature in features:
                if feature.lower() not in Query.__selectable_features__:
                    raise ValueError(
                      "Currently only featureclasses {} are supported.".format(
                        "/".join(Query.__selectable_features__)))
        else:
            featureclass = ",".join(Query.__selectable_features__)

        return self._print(study=study,
                           pathogen=pathogen,
                           library=library,
                           design=design,
                           replicate=replicate,
                           plate=plate,
                           featureclass=featureclass)

    def query(self,
              file_name=None,
              study=None,
              pathogen=None,
              library=None,
              design=None,
              replicate=None,
              plate=None,
              gene=None,
              sirna=None,
              well=None,
              featureclass=None,
              sample=None):
        """
        Query a database of image-based RNAi screening features for
         cells/bacteria/nuclei.
        The query can use filters, so that only a subset is selected.
        A lazy result set is returned, i.e. a set of plate files that meets the
        filtered criteria.

        :param study: filters by study, e.g.
         'infectx'/'group_cossart'/'infectx_published'
        :param pathogen: filters by pathogen, e.g.
         'salmonella'/'adeno'/'bartonella'/'brucella'/'listeria'
        :param library: filters by library, e.g. 'a'/'d'/'q'
        :param design: filters by design, e.g.: 'p'/'u'
        :param replicate: filters by replicate, i.e. a number
        :param plate: filters by plate, i.e.: 'dz44-1l'
        :param gene: filters by gene, i.e.: 'star'
        :param sirna: filters by gene, i.e.: 'l-019369-00'
        :param well: filters by gene, i.e.: 'a01'
        :param featureclass: filters by featureclass,
         e.g. 'nuclei'/'cells'/'bacteria'
        :param sample: sample from every well x times

        :return: returns a lazy ResultSet
        :rtype: ResultSet
        """

        # TODO put this to another place
        if featureclass is not None:
            features = featureclass.split(",")
            for feature in features:
                if feature.lower() not in Query.__selectable_features__:
                    raise ValueError(
                      "Currently only featureclasses {} are supported.".format(
                        "/".join(Query.__selectable_features__)))
        else:
            featureclass = ",".join(Query.__selectable_features__)

        return self._query(file_name,
          sample=sample,
                           study=study,
                           pathogen=pathogen,
                           library=library,
                           design=design,
                           replicate=replicate,
                           plate=plate,
                           gene=gene,
                           sirna=sirna,
                           well=well,
                           featureclass=featureclass)

    def insert(self, path):
        """
        Insert meta information of an platewise RNAi screen to a database.
        For insertion the path leading to the meta files has to be provided.
        Meta information is then written to either a sqlite database if `db`
        is set, otherwise the DB connection defaults to a postgres DB that
        listens on port 5432/.

        :param path: the folder to the meta files
        :type path: str
        :param db: filename of the sqlite database. If not set defaults to
         postgres DB.
        :type db: str
        :return:
        """

        with DBMS(self._db) as d:
            d.insert(path)

    def select(self, select,
               study=None,
               pathogen=None,
               library=None,
               design=None,
               replicate=None,
               plate=None,
               gene=None,
               sirna=None,
               well=None,
               featureclass=None):
        """
        Submits a select query to a database of image-based RNAi screening meta
        features to get an overview over meta information. The query returns
        the result as a list of strings.

        Parameter <i>select</i> can be any of the following choices:
          * study
          * pathogen
          * library
          * design
          * gene
          * sirna
          * well
          * featureclass

        :param select: the meta feature to select
        :type select: str
        :param study: filters by study, e.g.
         'infectx'/'group_cossart'/'infectx_published'
        :type study: str
        :param pathogen: filters by pathogen, e.g.
         'salmonella'/'adeno'/'bartonella'/'brucella'/'listeria'
         :type pathogen: str
        :param library: filters by library, e.g. 'a'/'d'/'q'
        :type library: str
        :param design: filters by design, e.g.: 'p'/'u'
        :type design: str
        :param replicate: filters by replicate, i.e. a number
        :type replicate: str
        :param plate: filters by plate, i.e.: 'dz44-1l'
        :type plate: str
        :param gene: filters by gene, i.e.: 'star'
        :type gene: str
        :param sirna: filters by gene, i.e.: 'l-019369-00'
        :type select: str
        :param sirna: filters by gene, i.e.: 'a01'
        :type well: str
        :param featureclass: filters by featureclass,
         e.g. 'nuclei'/'cells'/'bacteria'
        :type featureclass: str
        :return: returns a list of strings from the query
        :rtype: list(str)
        """

        return self._select(select,
                            study=study,
                            pathogen=pathogen,
                            library=library,
                            design=design,
                            replicate=replicate,
                            plate=plate,
                            gene=gene,
                            sirna=sirna,
                            well=well,
                            featureclass=featureclass)

    def _print(self, **kwargs):
        fls = self._table.print(**kwargs)
        return fls

    def _query(self, file_name, **kwargs):
        fls = self._table.filter(file_name, **kwargs)
        return ResultSet(fls, **kwargs)

    def _select(self, select, **kwargs):
        # check if the value to select for is correct
        if select not in Query.__filterable_features__:
            raise ValueError(
              "Please provide one of: ({})"
                  .format(",".join(Query.__filterable_features__)))
        # check if user provided a filter for X that also is selected for
        for k, v in kwargs.items():
            if k == select and v is not None:
                raise ValueError(
                  "You are selecting and filtering on '{}' "
                  "at the same time. Drop the filter.".format(select))

        with DBMS(self._db) as d:
            res = d.select(select, **kwargs)
        return res
