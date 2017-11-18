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
import re
import yaml
from pathlib import Path

from rnaiutilities.library_plate_layout import LibraryPlateLayout
from rnaiutilities.utility.check import check_feature_group
from rnaiutilities.utility.files import data_filename, meta_filename

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlateWriter:
    """
    Write a plate to tsv or any other format.
    """

    __NA__ = "NA"
    _meta_ = ["well", "gene", "sirna", "well_type", "image_idx", "object_idx"]
    _well_regex = re.compile("(\w)(\d+)")

    def __init__(self, layout_file):
        self._layout = LibraryPlateLayout(layout_file)

    def write(self, pfs, feature_groups, mapping):
        logger.info(
          "Integrating plate file set: {}".format(str(pfs.classifier)))
        for k, v in feature_groups.items():
            self._write(pfs, k, v, mapping)
        return 0

    def _write(self, pfs, feature_group, features, mapping):
        layout = self._get_layout(pfs)
        if layout is None and pfs.pathogen.lower() != "mock":
            logger.warning("Could not load layout for: " + pfs.classifier)
            return
        self._write_file(pfs, sorted(features, key=lambda x: x.short_name),
                         feature_group, mapping, layout)

    def _get_layout(self, pfs):
        return self._layout.get(
          pfs.pathogen, pfs.library, pfs.design, pfs.screen,
          pfs.replicate, pfs.plate, pfs.suffix)

    def _write_file(self, pfs, features, feature_group, mapping, layout):
        filename = pfs.outfile + "_" + feature_group
        try:
            if not Path(data_filename(filename)).exists():
                logger.info("Writing to: {}".format(filename))
                self._dump(filename, features, mapping, layout)
                logger.info("Success!")
            else:
                logger.info("{} already exists. Skipping.".format(filename))
        except Exception as e:
            logger.error(
              "Could not integrate {} with error {}".format(filename, str(e)))

    def _dump(self, filename, features, mapping, layout):
        check_feature_group(features)
        feature_names = [feat.featurename.lower() for feat in features]
        header = PlateWriter._meta_ + feature_names
        dat_file = data_filename(filename)

        meat_hash = {}
        with open(dat_file, "w") as f:
            f.write("\t".join(header) + "\n")
            nimg = features[0].values.shape[0]
            assert nimg == len(mapping)
            self._dump_images(
              nimg, layout, mapping, features, f, header, meat_hash)
        self._write_meta(filename, meat_hash, feature_names)

        return 0

    def _dump_images(self, nimg, layout, mapping, features, f, header, meat):
        meta = [PlateWriter.__NA__] * len(PlateWriter._meta_)
        for iimg in range(nimg):
            well = mapping[iimg]
            meta[0] = well
            if layout is not None:
                meta[1] = layout.gene(well)
                meta[2] = layout.sirna(well)
                meta[3] = layout.welltype(well)
            meta[4] = iimg + 1
            meat[";".join(map(str, meta[:4]))] = 1
            self._dump_cells(features, iimg, meta, f, header)

    @staticmethod
    def _dump_cells(features, iimg, meta, f, header):
        for cell in range(features[0].ncells[iimg]):
            vals = [PlateWriter.__NA__] * len(features)
            for p, _ in enumerate(features):
                try:
                    vals[p] = features[p].values[iimg, cell]
                except IndexError:
                    vals[p] = PlateWriter.__NA__
            meta[5] = cell + 1
            try:
                f.write("\t".join(list(map(str, meta)) +
                                  list(map(str, vals))).lower() + "\n")
            except Exception:
                f.write("\t".join([PlateWriter.__NA__] * len(header)) + "\n")

    @staticmethod
    def _write_meta(filename, meat_hash, features):
        h = {'elements': list(meat_hash.keys()),
             'features': features}

        meat_file = meta_filename(filename)
        try:
            with open(meat_file, "w") as m:
                yaml.dump(h, m, default_flow_style=False)
        except Exception as e:
            logger.error(
              "Some IO-error writing to meta file: {}".format(meat_file))
            logger.error(str(e))
