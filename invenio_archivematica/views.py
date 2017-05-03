# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio 3 module to connect Invenio to Archivematica."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from __future__ import absolute_import, print_function

from flask import Blueprint, render_template
from flask_babelex import gettext as _

from invenio_archivematica.api import create_accessioned_id

blueprint = Blueprint(
    'invenio_archivematica',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix="/oais"
)


@blueprint.route("/")
def index():
    """Show the index."""
    return render_template(
        "invenio_archivematica/index.html",
        module_name=_('Invenio-Archivematica'))


@blueprint.route("/test/<string:pid>/")
def test(pid):
    """Show a test page."""
    return """<DOCTYPE html><html><head></head><body>
    <h1>{}</h1>
    </body></html>""".format(create_accessioned_id(pid, 'recid'))
