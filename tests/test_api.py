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

"""Test the API."""

import uuid

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from invenio_archivematica import api


def test_create_accessioned_id(db):
    """Test ``create_accessioned_id`` function."""
    # First, we create a record
    recid = uuid.uuid4()
    PersistentIdentifier.create(
        'recid',
        '42',
        object_type='rec',
        object_uuid=recid,
        status=PIDStatus.REGISTERED)
    Record.create({'title': 'record test'}, recid)
    accessioned_id = api.create_accessioned_id('42', 'recid')
    assert accessioned_id == 'CERN-recid-42-0'
