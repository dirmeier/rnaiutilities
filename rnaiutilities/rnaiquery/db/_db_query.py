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

from ._db_setup import DatabaseInserter
from ..filesets.table_file import TableFile
from ..globals import FEATURECLASS
from ..globals import GENE, SIRNA, LIBRARY, DESIGN
from ..globals import REPLICATE, PLATE, STUDY, PATHOGEN

logging.basicConfig(
  level=logging.WARNING,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class DatabaseQuery:
    _gsw_ = [GENE, SIRNA]
    _descr_ = [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE, FEATURECLASS]

    def __init__(self, connection):
        self.__connection = connection

    def select(self, select):
        q = self._build_select_statement(select)
        logger.info(q)
        res = self.__connection.query(q)
        return res

    def query(self, **kwargs):
        q = self._build_query(**kwargs)
        logger.info(q)
        res = self._query(q, **kwargs)
        return res

    def _query(self, q, **kwargs):
        res = self.__connection.query(q)
        fls = {TableFile(x, self._feature_query(x[-1]), **kwargs) for x in res}
        return fls

    def _build_query(self, **kwargs):
        mq = self._build_meta_query(**kwargs)
        gq = self._build_plate_query(GENE, **kwargs)
        sq = self._build_plate_query(SIRNA, **kwargs)
        su = None
        if gq is not None and sq is not None:
            su = "JOIN (SELECT a1.filename \n" + \
                 "\t\tFROM ({}) a1 \n".format(gq) + \
                 "\t\tJOIN ({}) a2 \n".format(sq) + \
                 "\t\tON (a1.filename = a2.filename) \n" + \
                 "\t) a2"
        elif gq:
            su = "JOIN ({}) a2".format(gq)
        elif sq:
            su = "JOIN ({}) a2".format(sq)
        if su:
            q = "\nSELECT * \n" \
                "\tFROM ({}) a1 \n".format(mq) + \
                "\t" + su + " \n" \
                            "\tON (a1.filename = a2.filename);"
        else:
            q = mq + ";"
        return q

    @staticmethod
    def _build_meta_query(**kwargs):
        s = "SELECT * FROM meta"
        ar = []
        for k, v in kwargs.items():
            if v is not None:
                if k in DatabaseQuery._descr_:
                    ar.append("{}='{}'".format(k, v))
        if len(ar) > 0:
            s += " WHERE " + " and ".join(ar)
        return s

    @staticmethod
    def _build_plate_query(el, **kwargs):
        s = None
        if el in kwargs.keys():
            if kwargs[el] is not None:
                s = "SELECT filename FROM {} WHERE {}='{}'" \
                    .format(el, el, kwargs[el])
        return s

    def _feature_query(self, filename):
        d = DatabaseInserter.feature_table_name(filename)
        res = self.__connection.query("SELECT * FROM {}".format(d))
        res = list(map(lambda x: x[0], res))
        return res

    def _build_select_statement(self, select):
        if select in ["gene", "sirna", "well"]:
            return "SELECT distinct({}) from {};".format(select, select)
        else:
            return "SELECT distinct({}) from meta;".format(select)



