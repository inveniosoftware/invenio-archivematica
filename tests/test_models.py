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

"""Test the models."""

import uuid

from invenio_records.api import Record

from invenio_archivematica.models import Archive, ArchiveStatus


def test_ArchiveStatus():
    """Test the ArchiveStatus enumeration."""
    status = ArchiveStatus.IGNORED
    assert status == ArchiveStatus.IGNORED
    assert status != ArchiveStatus.DELETED
    assert status == 'IGNORED'
    assert str(status) == 'IGNORED'
    assert status.title == 'Ignored'


def test_Archive(db):
    """Test the Archive model class."""
    assert Archive.query.count() == 0
    # we create a record, it will automatically create an Archive via signals
    recid = uuid.uuid4()
    rec = Record.create({'title': 'This is a fake!'}, recid)
    db.session.commit()

    assert Archive.query.count() == 1
    ark = Archive.get_from_record(recid)
    assert ark.record == rec.model
    assert ark.status == ArchiveStatus.NEW
    assert ark.aip_accessioned_id is None
    assert ark.aip_id is None
    # let's change the object
    ark.status = ArchiveStatus.REGISTERED
    ark.aip_accessioned_id = '08'
    ark.aip_id = recid
    db.session.commit()
    ark = Archive.get_from_record(recid)
    assert ark.status == ArchiveStatus.REGISTERED
    assert ark.aip_accessioned_id == '08'
    assert ark.aip_id == recid
    # we try to get a non existing record
    assert Archive.get_from_record(uuid.uuid4()) is None
