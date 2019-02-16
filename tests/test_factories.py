# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test the factories."""

import json
from os import path
from uuid import uuid4

from flask import current_app
from invenio_files_rest.models import FileInstance
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_sipstore.models import SIP, RecordSIP, SIPFile, SIPMetadata, \
    SIPMetadataType
from six import BytesIO
from werkzeug.utils import import_string

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


def test_transfer_cp(app, db, locations):
    """Test factories.transfer_cp function."""
    # config
    app.config['SIPSTORE_ARCHIVER_DIRECTORY_BUILDER'] = \
        'helpers:archive_directory_builder'
    app.config['SIPSTORE_ARCHIVER_METADATA_TYPES'] = ['test']

    # SIP
    sip = SIP.create()

    # SIPFile
    f = FileInstance.create()
    fcontent = b'weighted companion cube\n'
    f.set_contents(BytesIO(fcontent), default_location=locations['archive'].uri)
    sfile = SIPFile(sip=sip, file=f, filepath='portal.txt')
    db.session.add(sfile)
    db.session.commit()

    #RecordSIP
    rec_uuid = uuid4()
    pid = PersistentIdentifier.create(
        'rec', '1', status=PIDStatus.REGISTERED, object_type='rec',
        object_uuid=rec_uuid)
    r_sip = RecordSIP(sip=sip, pid=pid) 

    # EXPORT
    factories.transfer_cp(sip.id, None)

    # TEST
    folder = path.join(locations['archive'].uri, 'test')
    assert path.isdir(folder)
    assert path.isfile(path.join(folder, 'data/portal.txt'))
    assert path.isdir(path.join(folder, 'metadata'))
    assert path.isfile(path.join(folder, 'metadata', 'metadata.csv'))
    with open(path.join(folder, 'data/portal.txt'), 'rb') as fp:
        assert fp.read() == fcontent
    with open(path.join(folder, 'metadata', 'metadata.csv'), 'r') as fp:
        assert fp.readline() == 'filename,dc.identifier\n'
        assert fp.readline() == 'objects/data,1\n'


def test_transfer_rsync(app, db, locations):
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
    f.set_contents(BytesIO(fcontent), default_location=locations['archive'].uri)
    sfile = SIPFile(sip=sip, file=f, filepath='portal.txt')
    db.session.add(sfile)
    db.session.commit()

    #RecordSIP
    rec_uuid = uuid4()
    pid = PersistentIdentifier.create(
        'rec', '1', status=PIDStatus.REGISTERED, object_type='rec',
        object_uuid=rec_uuid)
    r_sip = RecordSIP(sip=sip, pid=pid) 

    # EXPORT
    folder = path.join(locations['archive'].uri, 'lulz')
    params = {
        'server': '',
        'user': '',
        'destination': folder,
        'args': '-az'
    }
    factories.transfer_rsync(sip.id, params)

    # TEST
    assert not path.exists(path.join(locations['archive'].uri, 'test'))
    assert path.isdir(folder)
    assert path.isfile(path.join(folder, 'data/portal.txt'))
    assert path.isdir(path.join(folder, 'metadata'))
    assert path.isfile(path.join(folder, 'metadata', 'metadata.csv'))
    with open(path.join(folder, 'data/portal.txt'), 'rb') as fp:
        assert fp.read() == fcontent
    with open(path.join(folder, 'metadata', 'metadata.csv'), 'r') as fp:
        assert fp.readline() == 'filename,dc.identifier\n'
        assert fp.readline() == 'objects/data,1\n'
