# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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


def test_listeners_when_no_archivable_sip(app, db):
    """Test listener_sip_created and listener_record_updated functions."""
    # first we change the is_archivable function to return False
    app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY'] = 'invenio_archivematica.factories.is_archivable_none'

    assert Archive.query.count() == 0
    # let's create an SIP
    user = create_test_user('test@example.org')
    sip = SIP.create(True, user_id=user.id, agent={'test': 'test'})
    db.session.commit()

    assert Archive.query.count() == 1
