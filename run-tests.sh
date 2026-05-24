#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

pydocstyle invenio_archivematica tests docs && \
isort -rc -c -df && \
check-manifest --ignore ".travis-*" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
