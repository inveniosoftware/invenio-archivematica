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

from functools import partial, wraps

import requests
from flask import Blueprint, abort, current_app, jsonify, make_response, \
    render_template
from flask_babelex import gettext as _
from invenio_rest import ContentNegotiatedMethodView
from webargs import fields
from webargs.flaskparser import use_kwargs

from invenio_archivematica.api import fail_transfer, finish_transfer, \
    process_transfer
from invenio_archivematica.factories import create_accession_id
from invenio_archivematica.models import Archive, ArchiveStatus

blueprint = Blueprint(
    'invenio_archivematica',
    __name__,
    url_prefix="/oais"
)

# TODO remove
b = Blueprint(
    'invenio_archivematica',
    __name__,
    url_prefix="/oais",
    template_folder='templates'
)


@b.route("/")
def index():
    """Show the index."""
    return render_template(
        "invenio_archivematica/index.html",
        module_name=_('Invenio-Archivematica'))


@b.route("/test/<string:pid>/")
def test(pid):
    """Show a test page."""
    return """<DOCTYPE html><html><head></head><body>
    <h1>{}</h1>
    </body></html>""".format(create_accession_id(pid, 'recid'))


def pass_accession_id(f):
    """Decorate to retrieve an Archive object."""
    @wraps(f)
    def decorate(*args, **kwargs):
        aip_accession_id = kwargs.pop('aip_accession_id')
        archive = Archive.get_from_accession_id(aip_accession_id)
        if not archive:
            abort(404, 'Accession_id {} not found.'.format(aip_accession_id))
        return f(archive=archive, *args, **kwargs)
    return decorate


def validate_status(status):
    """Accept only valid status."""
    if status not in {'PROCESSING', 'REGISTERED', 'FAILED', 'DELETED'}:
        return False
    return True


class Status(ContentNegotiatedMethodView):
    """Status of the archival of a record."""

    def __init__(self, **kwargs):
        """Constructor."""
        kwargs['method_serializers'] = {
            'GET': {'application/json': make_response}
        }
        kwargs['default_method_media_type'] = {'GET': 'application/json'}
        kwargs['default_media_type'] = 'application/json'
        super(Status, self).__init__(**kwargs)

    @pass_accession_id
    @use_kwargs({
        'status': fields.Str(
            load_from='status',
            required=True,
            location='json',
            validate=validate_status
        ),
        'aip_id': fields.Str(
            load_from='uuid',
            location='json'
        )
    })
    def put(self, archive, status, aip_id=None):
        """Change the status of an Archive object.

        Should be used by the Archivematica Automation-Tool only.
        :params str aip_accession_id: accession_id of the AIP, used to find
        the corresponding Archive object. In the URL
        :params str status: the status of the AIP. One of the following:

        * PROCESSING
        * REGISTERED
        * FAILED
        * DELETED

        :params str aip_id: the IP of the AIP (optional)
        """
        if archive.status == status:
            return jsonify('')

        functions = {
            'PROCESSING': partial(process_transfer, aip_id=aip_id),
            'REGISTERED': partial(finish_transfer, aip_id=aip_id),
            'FAILED': fail_transfer,
            # TODO
            'DELETED': lambda x: "NIY.",
        }
        functions[status.name](archive.record)
        return jsonify(''), 200

    @pass_accession_id
    @use_kwargs({
        'real_status': fields.Boolean(
            load_from='realStatus',
            required=False,
            location='json'
        )
    })
    def get(self, archive, real_status=False):
        """Returns the status of the Archive object."""
        if not real_status \
                or archive.status == ArchiveStatus.FAILED \
                or not archive.aip_id:
            return jsonify(archive.status.value)
        # we ask Archivematica
        # first we look at the status of the transfer
        url = '{base}/api/transfer/status/{uuid}/'.format(
            base=current_app.config['ARCHIVEMATICA_DASHBOARD_URL'],
            uuid=archive.aip_id)
        params = {
            'username': current_app.config['ARCHIVEMATICA_DASHBOARD_USER'],
            'api_key': current_app.config['ARCHIVEMATICA_DASHBOARD_API_KEY']
        }
        response = requests.get(url, params=params)
        if response.ok:
            json = response.json()
            return jsonify(json['status'])
        # we try to get the status of the SIP
        url = '{base}/api/ingest/status/{uuid}/'.format(
            base=current_app.config['ARCHIVEMATICA_DASHBOARD_URL'],
            uuid=archive.aip_id)
        response = requests.get(url, params=params)
        if not response.ok:  # problem
            return jsonify(None), response.status_code
        # TODO update archive object
        json = response.json()
        return jsonify(json['status'])


blueprint.add_url_rule(
    '/status/<string:aip_accession_id>/',
    view_func=Status.as_view('status')
)
