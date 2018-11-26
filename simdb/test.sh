#!/usr/bin/env bash

# requires pytest
# pip install pytest

PYTHONPATH=$(realpath ..)
export PYTHONPATH

echo "Test $(python2 --version)"
python2 -m pytest --color=yes -v test

echo "Test $(python3 --version)"
python3 -m pytest --color=yes -v test