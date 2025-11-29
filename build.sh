#!/bin/bash
set -e


echo "Building package..."
python3 -m build


echo "Installing..."
pip install .