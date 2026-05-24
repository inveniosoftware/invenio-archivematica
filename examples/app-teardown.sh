#!/bin/sh
# SPDX-FileCopyrightText: 2017 CERN.
# SPDX-License-Identifier: MIT

# quit on errors:
set -o errexit

# quit on unbound symbols:
set -o nounset

DIR=`dirname "$0"`

cd $DIR
export FLASK_APP=app.py

# Teardown app
flask db destroy --yes-i-know
[ -e "$DIR/instance" ] && rm -Rf $DIR/instance
