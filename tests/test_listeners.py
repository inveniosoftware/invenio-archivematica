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

import pytest
from invenio_accounts.testutils import create_test_user
from invenio_sipstore.api import SIP

from invenio_archivematica.models import Archive, ArchiveStatus

testdata = [
    ('invenio_archivematica.factories.is_archivable_default',
     ArchiveStatus.NEW),
    ('invenio_archivematica.factories.is_archivable_none',
     ArchiveStatus.IGNORED)
]


@pytest.mark.parametrize("conf,expected_status", testdata)
def test_listeners(conf, expected_status, app, db):
    """Test listener_sip_created and listener_record_updated functions."""
    # first we change the is_archivable function
    app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY'] = conf

    assert Archive.query.count() == 0
    # let's create an SIP
    user = create_test_user('test@example.org')
    sip = SIP.create(True, user_id=user.id, agent={'test': 'test'})
    db.session.commit()

    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.sip.user.id == sip.user.id
    assert ark.status == expected_status
