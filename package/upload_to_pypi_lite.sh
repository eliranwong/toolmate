#!/usr/bin/env bash
# pip install wheel twine
python3 setup_lite.py sdist bdist_wheel
twine upload dist/*