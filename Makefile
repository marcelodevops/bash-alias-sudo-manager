.PHONY: build install clean


build:
python3 -m build


install:
pip install .


clean:
rm -rf dist build *.egg-info