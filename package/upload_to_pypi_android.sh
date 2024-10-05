#!/usr/bin/env bash
# pip install wheel twine
python3 setup_android.py sdist bdist_wheel
twine upload dist/*