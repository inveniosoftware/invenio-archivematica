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

"""Test the factories."""

import json
from os import path

from flask import current_app
from invenio_files_rest.models import FileInstance
from invenio_sipstore.models import SIP, SIPFile, SIPMetadata, SIPMetadataType
from six import BytesIO

from invenio_archivematica import factories
from invenio_archivematica.models import Archive


def test_create_accessioned_id(db):
    """Test ``create_accessioned_id`` function."""
    # First, we create a SIP
    sip = SIP.create()
    ark = Archive.create(sip)
    db.session.commit()
    accessioned_id = factories.create_accession_id(ark)
    assert accessioned_id \
        == current_app.config['ARCHIVEMATICA_ORGANIZATION_NAME'] + '-' \
        + str(sip.id)


def test_is_archivable_default(db):
    """Test ``is_archivable_default`` function."""
    sip1 = SIP.create(archivable=True)
    sip2 = SIP.create(archivable=False)
    assert factories.is_archivable_default(sip1)
    assert not factories.is_archivable_default(sip2)


def test_is_archivable_none(db):
    """Test ``is_archivable_none`` function."""
    sip1 = SIP.create(archivable=True)
    sip2 = SIP.create(archivable=False)
    assert not factories.is_archivable_none(sip1)
    assert not factories.is_archivable_none(sip2)


def test_transfer_cp(app, db, location):
    """Test factories.transfer_cp function."""
    # config
    app.config['SIPSTORE_ARCHIVER_DIRECTORY_BUILDER'] = \
        'helpers:archive_directory_builder'
    app.config['SIPSTORE_ARCHIVER_METADATA_TYPES'] = ['test']
    # SIP
    sip = SIP.create()
    # SIPMetadataType
    mtype = SIPMetadataType(title='Test', name='test', format='json')
    db.session.add(mtype)
    # SIPMetadata
    mcontent = {'title': 'title', 'author': 'me'}
    meth = SIPMetadata(sip=sip, type=mtype, content=json.dumps(mcontent))
    db.session.add(meth)
    # SIPFile
    f = FileInstance.create()
    fcontent = b'weighted companion cube\n'
    f.set_contents(BytesIO(fcontent), default_location=location.uri)
    sfile = SIPFile(sip=sip, file=f, filepath='portal.txt')
    db.session.add(sfile)
    db.session.commit()

    # EXPORT
    factories.transfer_cp(sip.id, None)

    # TEST
    folder = path.join(location.uri, 'test')
    assert path.isdir(folder)
    assert path.isdir(path.join(folder, 'files'))
    assert path.isfile(path.join(folder, 'files', 'portal.txt'))
    assert path.isdir(path.join(folder, 'metadata'))
    assert path.isfile(path.join(folder, 'metadata', 'test.json'))
    with open(path.join(folder, 'files', 'portal.txt'), 'rb') as fp:
        assert fp.read() == fcontent
    with open(path.join(folder, 'metadata', 'test.json'), 'r') as fp:
        assert json.loads(fp.read()) == mcontent


def test_transfer_rsync(app, db, location):
    """Test factories.transfer_rsync function."""
    # config
    app.config['SIPSTORE_ARCHIVER_DIRECTORY_BUILDER'] = \
        'helpers:archive_directory_builder'
    app.config['SIPSTORE_ARCHIVER_METADATA_TYPES'] = ['test']
    # SIP
    sip = SIP.create()
    # SIPMetadataType
    mtype = SIPMetadataType(title='Test', name='test', format='json')
    db.session.add(mtype)
    # SIPMetadata
    mcontent = {'title': 'title', 'author': 'me'}
    meth = SIPMetadata(sip=sip, type=mtype, content=json.dumps(mcontent))
    db.session.add(meth)
    # SIPFile
    f = FileInstance.create()
    fcontent = b'weighted companion cube\n'
    f.set_contents(BytesIO(fcontent), default_location=location.uri)
    sfile = SIPFile(sip=sip, file=f, filepath='portal.txt')
    db.session.add(sfile)
    db.session.commit()

    # EXPORT
    folder = path.join(location.uri, 'lulz')
    params = {
        'server': '',
        'user': '',
        'destination': folder,
        'args': '-az'
    }
    factories.transfer_rsync(sip.id, params)

    # TEST
    assert not path.exists(path.join(location.uri, 'test'))
    assert path.isdir(folder)
    assert path.isdir(path.join(folder, 'files'))
    assert path.isfile(path.join(folder, 'files', 'portal.txt'))
    assert path.isdir(path.join(folder, 'metadata'))
    assert path.isfile(path.join(folder, 'metadata', 'test.json'))
    with open(path.join(folder, 'files', 'portal.txt'), 'rb') as fp:
        assert fp.read() == fcontent
    with open(path.join(folder, 'metadata', 'test.json'), 'r') as fp:
        assert json.loads(fp.read()) == mcontent
