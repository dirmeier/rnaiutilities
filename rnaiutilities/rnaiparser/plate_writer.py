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
from pathlib import Path
from rnaiutilities.rnaiparser.utility import check_feature_group

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__NA__ = "NA"


class PlateWriter:
    """
    Write a plate to tsv or any other format.
    """

    _meta_ = ["well", "gene", "sirna", "well_type", "image_idx", "object_idx"]
    _well_regex = re.compile("(\w)(\d+)")

    def __init__(self, layout):
        self._layout = layout

    def write(self, pfs, feature_groups, mapping):
        logger.info("Integrating the different feature sets to matrices for "
                    "plate file set: " + str(pfs.classifier))
        for k, v in feature_groups.items():
            self._write(pfs, k, v, mapping)
        return 0

    def _write(self, pfs, feature_group, features, mapping):
        features = sorted(features, key=lambda x: x.short_name)
        pathogen = pfs.pathogen
        library = pfs.library
        replicate = pfs.replicate
        screen = pfs.screen
        design = pfs.design
        plate = pfs.plate
        suffix = pfs.suffix
        layout = self._layout.get(pathogen, library, design,
                                  screen, replicate, plate, suffix)
        if layout is None and pfs.pathogen.lower() != "mock":
            logger.warning("Could not load layout for: " + pfs.classifier)
            return
        filename = pfs.outfile + "_" + feature_group
        try:
            if not Path(self.data_filename(filename)).exists():
                logger.info("Writing to: {}".format(filename))
                self._write_file(filename, features, mapping, layout)
                logger.info("Success: {}".format(filename))
            else:
                logger.info(filename + " already exists. Skipping")
        except Exception as e:
            logger.error("Could not integrate: {}".format(filename))
            logger.error(str(e))

    def _write_file(self, filename, features, mapping, layout):
        check_feature_group(features)
        meat_hash = {}
        feature_names = [feat.featurename.lower() for feat in features]
        header = PlateWriter._meta_ + feature_names
        dat_file = self.data_filename(filename)

        meta = [__NA__] * len(PlateWriter._meta_)
        with open(dat_file, "w") as f:
            f.write("\t".join(header) + "\n")
            nimg = features[0].values.shape[0]
            assert nimg == len(mapping)
            for iimg in range(nimg):
                well = mapping[iimg]
                meta[0] = well
                if layout is not None:
                    meta[1] = layout.gene(well)
                    meta[2] = layout.sirna(well)
                    meta[3] = layout.welltype(well)
                meta[4] = iimg + 1
                meat_hash[";".join(map(str, meta[:4]))] = 1
                for cell in range(features[0].ncells[iimg]):
                    vals = [__NA__] * len(features)
                    for p, _ in enumerate(features):
                        try:
                            vals[p] = features[p].values[iimg, cell]
                        except IndexError:
                            vals[p] = __NA__
                    meta[5] = cell + 1
                    try:
                        f.write("\t".join(list(map(str, meta)) +
                                          list(map(str, vals))).lower() + "\n")
                    except Exception:
                        f.write("\t".join([__NA__] * len(header)) + "\n")

        self._write_meta(filename, meat_hash, feature_names)
        return 0

    def _write_meta(self, filename, meat_hash, features):
        h = {'elements': list(meat_hash.keys()),
             'features': features}

        meat_file = self._meta_filename(filename)
        try:
            import yaml
            with open(meat_file, "w") as m:
                yaml.dump(h, m, default_flow_style=False)
        except Exception as e:
            logger.error("Some IO-error writing to meta file: {}"
                         .format(meat_file))
            logger.error(str(e))

    @staticmethod
    def data_filename(filename):
        return filename + "_data.tsv"

    @staticmethod
    def _meta_filename(filename):
        return filename + "_meta.tsv"
