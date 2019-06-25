# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test the tasks."""

import time
import uuid

from invenio_sipstore.models import SIP

from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.tasks import archive_new_sips, oais_fail_transfer, \
    oais_finish_transfer, oais_process_aip, oais_process_transfer, \
    oais_start_transfer


def test_oais_start_transfer(app, db, locations):
    """Test the oais_start_transfer function."""
    assert Archive.query.count() == 0
    # let's create a SIP
    sip = SIP.create()
    Archive.create(sip)
    db.session.commit()
    assert Archive.query.count() == 1
    # we start the transfer
    oais_start_transfer(sip.id, '1991')
    ark = Archive.get_from_sip(sip.id)
    assert ark.status == ArchiveStatus.WAITING
    assert ark.accession_id == '1991'
    # we try the case where no archive exist and transfer fails
    db.session.delete(ark)
    db.session.commit()
    app.config['ARCHIVEMATICA_TRANSFER_FACTORY'] = 'helpers:transfer_fail'
    assert Archive.query.count() == 0
    oais_start_transfer(sip.id, '1991')
    ark = Archive.get_from_sip(sip.id)
    assert Archive.query.count() == 1
    assert ark.status == ArchiveStatus.FAILED_TRANSFER
    assert ark.accession_id == '1991'
    assert ark.sip.archived is False


def test_oais_process_transfer(db):
    """Test the oais_process_transfer function."""
    # let's create a SIP
    sip = SIP.create()
    Archive.create(sip)
    db.session.commit()
    aipid = uuid.uuid4()
    oais_process_transfer(sip.id, archivematica_id=aipid)
    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.status == ArchiveStatus.PROCESSING_TRANSFER
    assert ark.archivematica_id == aipid


def test_oais_process_aip(db):
    """Test the oais_process_aip function."""
    # let's create a SIP
    sip = SIP.create()
    Archive.create(sip)
    aipid = uuid.uuid4()
    db.session.commit()
    # we fail the transfer
    oais_process_aip(sip.id, archivematica_id=aipid)
    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.status == ArchiveStatus.PROCESSING_AIP
    assert ark.archivematica_id == aipid


def test_oais_finish_transfer(db):
    """Test the oais_finish_transfer function."""
    # let's create a SIP
    sip = SIP.create()
    Archive.create(sip)
    aipid = uuid.uuid4()
    db.session.commit()
    # we finish the transfer
    oais_finish_transfer(sip.id, archivematica_id=aipid)
    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.status == ArchiveStatus.REGISTERED
    assert ark.archivematica_id == aipid
    assert ark.sip.archived is True


def test_oais_fail_transfer(db):
    """Test the oais_fail_transfer function."""
    # let's create a SIP
    sip = SIP.create()
    Archive.create(sip)
    db.session.commit()
    # we fail the transfer
    oais_fail_transfer(sip.id)
    assert Archive.query.count() == 1
    ark = Archive.get_from_sip(sip.id)
    assert ark.status == ArchiveStatus.FAILED_TRANSFER


def test_archive_new_sips(db, locations):
    """Test the archive_new_sips function."""
    # we create 2 SIP
    sip1 = SIP.create()
    Archive.create(sip1)
    db.session.commit()
    time.sleep(3)
    sip2 = SIP.create()
    Archive.create(sip2)
    db.session.commit()
    # we archive all records older than 2 seconds
    archive_new_sips('invenio_archivematica.factories.create_accession_id',
                     days=0, seconds=2, delay=False)
    arks = Archive.query.all()
    assert len(arks) == 2
    for ark in arks:
        if ark.sip_id == sip1.id:
            assert ark.status == ArchiveStatus.WAITING
            # we update the archive so it will be ignored in what follows
            ark.status = ArchiveStatus.IGNORED
            db.session.commit()
        else:
            assert ark.status == ArchiveStatus.NEW
    # now we archive everything, but rec2 shouldn't be archived as it is
    # flagged as IGNORED
    archive_new_sips('invenio_archivematica.factories.create_accession_id',
                     days=0, delay=False)
    arks = Archive.query.all()
    assert len(arks) == 2
    for ark in arks:
        if ark.sip_id == sip1.id:
            assert ark.status == ArchiveStatus.IGNORED
        else:
            assert ark.status == ArchiveStatus.WAITING
