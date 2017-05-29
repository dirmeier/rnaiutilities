# Copyright (C) 2016 Simon Dirmeier
#
# This file is part of tix_query.
#
# tix_query is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tix_query is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tix_query. If not, see <http://www.gnu.org/licenses/>.
#
#
# @author = 'Simon Dirmeier'
# @email = 'mail@simon-dirmeier.net'


import logging
from rnaiquery.controller import Controller

logging.basicConfig(
  level=logging.INFO,
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
logger = logging.getLogger(__name__)

class Query:
    def __init__(self, db=None):
        """
        Create an instance to query a data.base
        
        :param db: if provided the filename of a sqlite database
        :type db: str
        """
        self.__ctrl = Controller(db)

    def query(self,
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
              sample=100):
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

        if featureclass is None:
            logger.error("Currently using no featureclass it not supported.")
            exit(0)

        return self.__ctrl.query(sample=sample,
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

if __name__ == "__main__":
    q = Query()
    res = q.query(study="infectx",
                  well="a01", library="d",
                  replicate=1, featureclass="cells",
                  gene="atp6v1a", sirna="l-017590-01", sample=10)
    res.dump("/Users/simondi/Desktop/simon.h5")
