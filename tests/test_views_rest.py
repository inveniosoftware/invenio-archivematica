# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test the REST API."""

import json
import uuid

from flask import url_for
from invenio_sipstore.models import SIP
from mock import patch
from requests import Response

from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.views.rest import validate_status


def test_validate_status():
    """Test the function validate_status."""
    assert validate_status('SIP_PROCESSING') is True
    assert validate_status('lol') is False


def test_Archive_get_401(client):
    """Test the Archive's get method with no API key."""
    response = client.get(url_for(
        'invenio_archivematica_api.archive_api',
        accession_id='test'))
    assert response.status_code == 401


def test_Archive_get_404(client, oauth2):
    """Test the Archive's get method no existing Archive object."""
    response = client.get(url_for(
        'invenio_archivematica_api.archive_api',
        accession_id='unknown',
        access_token=oauth2.token))
    assert response.status_code == 404


def test_Archive_get_200(db, client, oauth2):
    """Test the Archive's get method with no archivematica_id."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    db.session.commit()

    response = client.get(url_for(
        'invenio_archivematica_api.archive_api',
        accession_id=ark.accession_id,
        access_token=oauth2.token))
    assert response.status_code == 200
    result = json.loads(response.data.decode('utf-8'))
    assert 'sip_id' in result and result['sip_id'] == str(sip.id)
    assert 'status' in result and result['status'] == 'NEW'
    assert 'accession_id' in result and result['accession_id'] == 'id'
    assert 'archivematica_id' in result \
        and result['archivematica_id'] == str(ark.archivematica_id)


def test_Archive_get_realstatus_transfer(db, client, oauth2):
    """Test the Archive's get method with transfer processing."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.WAITING
    db.session.commit()

    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps({
        'status': 'SIP_PROCESSING'
    }).encode('utf-8')
    with patch('requests.get', return_value=mock_response):
        response = client.get(url_for(
            'invenio_archivematica_api.archive_api',
            accession_id=ark.accession_id,
            access_token=oauth2.token),
                              data=json.dumps({'realStatus': True}),
                              content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data.decode('utf-8'))
    assert 'sip_id' in result and result['sip_id'] == str(sip.id)
    assert 'status' in result and result['status'] == 'PROCESSING_TRANSFER'
    assert 'accession_id' in result and result['accession_id'] == 'id'
    assert 'archivematica_id' in result \
        and result['archivematica_id'] == str(ark.archivematica_id)


def test_Archive_get_realstatus_ingest(db, client, oauth2):
    """Test the Archive's get method with ingest finished."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.WAITING
    db.session.commit()

    new_uuid = str(uuid.uuid4())
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps({'status': 'COMPLETE',
                                         'sip_uuid': new_uuid}).encode('utf-8')
    with patch('requests.get', return_value=mock_response):
        response = client.get(url_for(
            'invenio_archivematica_api.archive_api',
            accession_id=ark.accession_id,
            access_token=oauth2.token),
                              data=json.dumps({'realStatus': True}),
                              content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data.decode('utf-8'))
    assert 'sip_id' in result and result['sip_id'] == str(sip.id)
    assert 'status' in result and result['status'] == 'REGISTERED'
    assert 'accession_id' in result and result['accession_id'] == 'id'
    assert 'archivematica_id' in result \
        and result['archivematica_id'] == new_uuid


def test_Archive_get_status_code(db, client, oauth2):
    """Test the Archive's get method with error on Archivematica."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.WAITING
    db.session.commit()
    mock_response = Response()
    mock_response.status_code = 404
    with patch('requests.get', return_value=mock_response):
        response = client.get(url_for(
            'invenio_archivematica_api.archive_api',
            accession_id=ark.accession_id,
            access_token=oauth2.token),
                              data=json.dumps({'realStatus': True}),
                              content_type='application/json')
    assert response.status_code == mock_response.status_code


def test_Archive_patch_401(client):
    """Test the Archive's get method with no API key."""
    response = client.patch(url_for(
        'invenio_archivematica_api.archive_api',
        accession_id='test'))
    assert response.status_code == 401


def test_Archive_patch_200(db, client, oauth2):
    """Test the Archive's get method with no archivematica_id."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id')
    db.session.commit()

    params = {
        'archivematica_id': str(uuid.uuid4()),
        'status': 'COMPLETE'
    }
    response = client.patch(url_for(
        'invenio_archivematica_api.archive_api',
        accession_id=ark.accession_id,
        access_token=oauth2.token),
                            data=json.dumps(params),
                            content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data.decode('utf-8'))
    assert 'sip_id' in result and result['sip_id'] == str(sip.id)
    assert 'status' in result and result['status'] == 'REGISTERED'
    assert 'accession_id' in result and result['accession_id'] == 'id'
    assert 'archivematica_id' in result \
        and result['archivematica_id'] == params['archivematica_id']

    ark = Archive.query.one()
    assert ark.status == ArchiveStatus.REGISTERED
    assert str(ark.archivematica_id) == params['archivematica_id']


def test_ArchiveDownload_get_401(client):
    """Test the Download's get method with no API key."""
    response = client.get(url_for(
        'invenio_archivematica_api.download_api',
        accession_id='test'))
    assert response.status_code == 401


def test_ArchiveDownload_get_412(db, client, oauth2):
    """Test the Download's get method with no archivematica_id."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id')
    db.session.commit()

    response = client.get(url_for(
        'invenio_archivematica_api.download_api',
        accession_id=ark.accession_id,
        access_token=oauth2.token))
    assert response.status_code == 412


def test_ArchiveDownload_get_520(db, client, oauth2):
    """Test the Download's get method with no storage server running."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.REGISTERED
    db.session.commit()
    response = client.get(url_for(
        'invenio_archivematica_api.download_api',
        accession_id=ark.accession_id,
        access_token=oauth2.token))
    assert response.status_code == 520


def test_ArchiveDownload_get_status_code(db, client, oauth2):
    """Test the API request for Download's get method."""
    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.REGISTERED
    db.session.commit()
    mock_response = Response()
    mock_response.status_code = 404
    with patch('requests.get', return_value=mock_response):
        response = client.get(url_for(
            'invenio_archivematica_api.download_api',
            accession_id=ark.accession_id,
            access_token=oauth2.token))
    assert response.status_code == mock_response.status_code
