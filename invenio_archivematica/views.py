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

from __future__ import absolute_import, print_function

from functools import partial

from flask import Blueprint, abort, jsonify, render_template, request
from flask_babelex import gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from invenio_archivematica.api import create_accessioned_id, fail_transfer, \
    finish_transfer, process_transfer
from invenio_archivematica.models import ArchiveStatus

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


@blueprint.route("/set_status/<int:pid>/", methods=['POST'])
def set_status(pid):
    """Changes the status of an AIP.

    This needs to receive JSON with `status` key, and depending on the status,
    extra keys like `aip_id`...
    """
    try:
        resolver = Resolver(pid_type='recid', getter=Record.get_record)
        pid, record = resolver.resolve(pid)
    except PIDDoesNotExistError:
        abort(404)
    try:
        status = ArchiveStatus(request.values['status'])
    except KeyError as err:
        return jsonify(message="No key 'status' in data."), 400
    except ValueError as err:
        return jsonify(message=err.message), 400

    functions = {
        # can't mark as new: done by listeners
        'NEW': lambda x: "invalid method.",
        # can't mark as waiting: done by the factory when creating transfers
        'WAITING': lambda x: "invalid method.",
        'PROCESSING': process_transfer,
        'REGISTERED': partial(finish_transfer,
                              aip_id=request.values.get('aip_id')),
        'FAILED': fail_transfer,
        # can't mark as ignored: done by listeners
        'IGNORED': lambda x: "invalid method.",
        # TODO
        'DELETED': lambda x: "invalid method.",
    }
    ret = functions[status.name](record)
    if ret:
        return jsonify(message=ret), 400
    return '', 200
