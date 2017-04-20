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

"""Test the listeners."""

import uuid

import pytest
from invenio_records.api import Record

from invenio_archivematica.listeners import listener_record_created, \
    listener_record_updated
from invenio_archivematica.models import Archive, ArchiveStatus

testdata = [
    ('invenio_archivematica.factories.is_archivable_all',
     ArchiveStatus.NEW),
    ('invenio_archivematica.factories.is_archivable_none',
     ArchiveStatus.IGNORED)
]


@pytest.mark.parametrize("conf,expected_status", testdata)
def test_listeners(conf, expected_status, app, db):
    """Test listener_record_created and listener_record_updated functions."""
    # first we change the is_archivable function
    app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY'] = conf

    assert Archive.query.count() == 0
    # let's create a record
    recid = uuid.uuid4()
    rec = Record.create({'title': 'This is a fake!'}, recid)
    db.session.commit()

    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.record == rec.model
    assert ark.status == expected_status

    # we simulate that the record has been archived anyway :p
    ark.status = ArchiveStatus.REGISTERED
    db.session.add(ark)
    # now we update the record
    rec['author'] = 'ME'
    rec.commit()
    db.session.commit()
    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.status == expected_status

    # we delete the Archive object and update the record
    db.session.delete(ark)
    db.session.commit()
    assert Archive.query.count() == 0
    rec['summary'] = 'Very interesting book :)'
    rec.commit()
    db.session.commit()
    assert Archive.query.count() == 1
    ark = Archive.query.filter_by(record_id=recid).one()
    assert ark.status == expected_status
