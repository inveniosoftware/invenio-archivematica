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

"""Listeners connected to signals."""

from flask import current_app
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import import_string

from invenio_archivematica.models import Archive, ArchiveStatus


def listener_record_created(record, *args, **kwargs):
    """Create an entry in the database when a record is created."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    ark = Archive.create(record.model)
    if not is_archivable or not is_archivable(record):
        ark.status = ArchiveStatus.IGNORED
        db.session.add(ark)


def listener_record_updated(record, *args, **kwargs):
    """Create an entry in the database when a record is updated."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    # we test if the archive object already exists
    ark = Archive.get_from_record(record.id)
    # otherwise we create it
    if not ark:
        ark = Archive.create(record.model)
    # we check if we need to archive it or not
    if is_archivable and is_archivable(record):
        if ark.status != ArchiveStatus.NEW:
            ark.status = ArchiveStatus.NEW
            db.session.add(ark)
    else:
        if ark.status != ArchiveStatus.IGNORED:
            ark.status = ArchiveStatus.IGNORED
            db.session.add(ark)
