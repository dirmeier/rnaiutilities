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


import random


class PlateFileSet:
    """
    Class that stores filenames and meta info for a single plate.
    """

    def __init__(self, classifier, outfile, study, pathogen, library, design,
                 screen, replicate, suffix, plate):
        self._classifier = classifier
        self._outfile = outfile
        self._study = study
        self._pathogen = pathogen
        self._library = library
        self._design = design
        self._screen = screen
        self._replicate = replicate
        self._suffix = suffix
        self._plate = plate
        self._files = []
        # sirna-entrez mapping
        self._mapping = None

    def __iter__(self):
        for f in self._files:
            yield f

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\t".join([self._study, self._pathogen, self._library,
                          self._design, self._screen, self._replicate,
                          self._plate, self._suffix])

    def __len__(self):
        return len(self._files)

    @property
    def meta(self):
        return [self._study, self._pathogen, self._library, self._design,
                self._screen, self._replicate, self._suffix, self.plate]

    @property
    def pathogen(self):
        return self._pathogen

    @property
    def library(self):
        return self._library

    @property
    def design(self):
        return self._design

    @property
    def replicate(self):
        return self._replicate

    @property
    def screen(self):
        return self._screen

    @property
    def plate(self):
        return self._plate

    def sample(self, cnt):
        return random.sample(self._files, cnt)

    @property
    def classifier(self):
        return self._classifier

    @property
    def files(self):
        return self._files

    @property
    def outfile(self):
        return self._outfile

    @property
    def study(self):
        return self._study

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        self._mapping = value

    @property
    def suffix(self):
        return self._suffix

