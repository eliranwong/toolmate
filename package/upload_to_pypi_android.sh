#!/usr/bin/env bash
python3 setup_android.py sdist bdist_wheel
twine upload dist/*