#!/usr/bin/env bash

function install {
    pip uninstall rnaiutilities && pip install .
    exit
}

function test {
    rnai-query query --help
    rnai-parse parsereport --help
    coverage
    exit
}

function coverage {
    py.test --cov=./
    exit
}

CMD=$1
case "$CMD" in
  install)
    install
  ;;
  test)
    test
  ;;
  coverage)
    coverage
  ;;
  *)
  install
  test
esac
