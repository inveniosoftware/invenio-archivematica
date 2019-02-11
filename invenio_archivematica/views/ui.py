# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Archivematica user's views.

Here are writtent the views for the user, among others the view to create
the 'processingMCP.xml' file used by Archivematica.
"""

from flask import Blueprint, render_template
from flask_babelex import gettext as _

from invenio_archivematica.factories import create_accession_id
from invenio_archivematica.models import Archive

blueprint = Blueprint(
    'invenio_archivematica',
    __name__,
    url_prefix="/oais",
    template_folder='../templates'
)


@blueprint.route("/")
def index():
    """Show the index."""
    return render_template(
        "invenio_archivematica/index.html",
        module_name=_('Invenio-Archivematica'))


@blueprint.route("/test/<string:accession_id>/")
def test(accession_id):
    """Show a test page."""
    ark = Archive.get_from_accession_id(accession_id)
    return """<DOCTYPE html><html><head></head><body>
    <h1>{}</h1>
    </body></html>""".format(create_accession_id(ark))
