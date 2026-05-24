# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

"""Listeners connected to signals."""

from flask import current_app
from werkzeug.utils import import_string

from invenio_archivematica.models import Archive, ArchiveStatus


def listener_sip_created(sip, *args, **kwargs):
    """Create an entry in the database when a sip is created."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    ark = Archive.create(sip.model)
    if not is_archivable or not is_archivable(sip):
        ark.status = ArchiveStatus.IGNORED
