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

from .models import Archive, ArchiveStatus


def listener_record_created(record, *args, **kwargs):
    """Create an entry in the database when a record is created."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    if is_archivable and is_archivable(record):
        Archive.create(record.model)


def listener_record_updated(record, *args, **kwargs):
    """Create an entry in the database when a record is updated."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    if not is_archivable or not is_archivable(record):
        return
    # we test if the archive object already exists
    try:
        ark = Archive.query.filter_by(record_id=record.id).one()
        if ark.status != ArchiveStatus.NEW:
            ark.status = ArchiveStatus.NEW
            db.session.add(ark)
    # otherwise we create it
    except NoResultFound:
        Archive.create(record.model)
