import uuid
from collections import namedtuple

import pytest
from flask import make_response, url_for
from invenio_sipstore.models import SIP
from mock import patch
from requests import Response
from requests.exceptions import ConnectionError

from invenio_archivematica import InvenioArchivematica
from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.views import ArchiveDownload


def test_ArchiveDownload_get_412(app, db, client):
    """Test the Download's get method with no archivematica_id."""

    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id')
    db.session.commit()

    response = client.get(url_for(
        'invenio_archivematica_api.download_api',
        accession_id=ark.accession_id))
    assert response.status_code == 412


def test_ArchiveDownload_get_520(app, db, client):
    """Test the Download's get method with no storage server running."""

    sip = SIP.create()
    ark = Archive.create(sip=sip, accession_id='id',
                         archivematica_id=uuid.uuid4())
    ark.status = ArchiveStatus.REGISTERED
    db.session.commit()
    response = client.get(url_for(
        'invenio_archivematica_api.download_api',
        accession_id=ark.accession_id))
    assert response.status_code == 520


def test_ArchiveDownload_get_status_code(app, db, client):
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
            accession_id=ark.accession_id))
    assert response.status_code == mock_response.status_code
