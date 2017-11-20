#!/usr/bin/env bash

pip uninstall rnaiutilities && pip install .

rnai-query query --help
rnai-parse parsereport --help
py.test --cov=./