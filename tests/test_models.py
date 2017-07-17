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

from invenio_accounts.testutils import create_test_user
from invenio_sipstore.api import SIP

from invenio_archivematica.models import Archive, ArchiveStatus, \
    status_converter


def test_ArchiveStatus():
    """Test the ArchiveStatus enumeration."""
    status = ArchiveStatus.IGNORED
    assert status == ArchiveStatus.IGNORED
    assert status != ArchiveStatus.DELETED
    assert status == 'IGNORED'
    assert str(status) == 'IGNORED'
    assert status.title == 'Ignored'


def test_status_converter():
    """Test the ``status_converter`` function."""
    assert status_converter('COMPLETE') == ArchiveStatus.REGISTERED
    assert status_converter('PROCESSING') == ArchiveStatus.PROCESSING_TRANSFER
    assert status_converter('PROCESSING', True) == \
        ArchiveStatus.PROCESSING_AIP
    assert status_converter('USER_INPUT') == ArchiveStatus.FAILED


def test_Archive(db):
    """Test the Archive model class."""
    assert Archive.query.count() == 0
    # we create an SIP, it will automatically create an Archive via signals
    user = create_test_user('test@example.org')
    sip = SIP.create(True, user_id=user.id, agent={'test': 'test'})
    db.session.commit()

    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.sip.user.id == sip.user.id
    assert ark.status == ArchiveStatus.NEW
    assert ark.accession_id is None
    assert ark.archivematica_id is None
    # let's change the object
    ark.status = ArchiveStatus.REGISTERED
    ark.accession_id = '08'
    ark.archivematica_id = sip.id
    db.session.commit()
    ark = Archive.get_from_accession_id('08')
    assert Archive.query.count() == 1
    assert ark.status == ArchiveStatus.REGISTERED
    assert ark.archivematica_id == sip.id
    # we try to get a non existing record
    assert Archive.get_from_sip(uuid.uuid4()) is None
