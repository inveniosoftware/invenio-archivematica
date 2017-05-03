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

"""Test the tasks."""

import uuid

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.tasks import archive_record_failed_transfer, \
    archive_record_finish_transfer, archive_record_start_transfer


def test_archive_record_start_transfer(db):
    """Test the archive_record_start_transfer function."""
    assert Archive.query.count() == 0
    # let's create a record
    recid = uuid.uuid4()
    PersistentIdentifier.create(
        'recid',
        '1991',
        object_type='rec',
        object_uuid=recid,
        status=PIDStatus.REGISTERED)
    rec = Record.create({'title': 'Ponys VS Unicorns'}, recid)
    db.session.commit()
    # we start the transfer
    archive_record_start_transfer(recid)
    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.record == rec.model
    assert ark.status == ArchiveStatus.PROCESSING
    assert '1991' in ark.aip_accessioned_id


def test_archive_record_finish_transfer(db):
    """Test the test_archive_record_finish_transfer function."""
    # let's create a record
    recid = uuid.uuid4()
    aipid = uuid.uuid4()
    rec = Record.create({'title': 'Job finished'}, recid)
    db.session.commit()
    # we finish the transfer
    archive_record_finish_transfer(recid, aipid)
    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.status == ArchiveStatus.REGISTERED
    assert ark.aip_id == aipid


def test_archive_record_failed_transfer(db):
    """Test the test_archive_record_failed_transfer function."""
    # let's create a record
    recid = uuid.uuid4()
    aipid = uuid.uuid4()
    rec = Record.create({'title': 'Job finished'}, recid)
    db.session.commit()
    # we fail the transfer
    archive_record_failed_transfer(recid)
    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.status == ArchiveStatus.FAILED
