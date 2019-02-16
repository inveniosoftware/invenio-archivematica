# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test archiver."""

import time
from uuid import uuid4

from fs.opener import opener
from invenio_files_rest.models import FileInstance, Location
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_sipstore.models import SIP, RecordSIP, SIPFile
from six import BytesIO, b

from invenio_archivematica.archivers import ArchivematicaArchiver
from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.tasks import archive_new_sips, oais_fail_transfer, \
    oais_finish_transfer, oais_process_aip, oais_process_transfer, \
    oais_start_transfer


def test_write_all_files(app, db, archive_fs, sip):
    """Test saving files by Archivematica Archiver."""

    archiver = ArchivematicaArchiver(sip)

    assert not archive_fs.listdir()

    archiver.write_all_files()
    fs = archive_fs.opendir(archiver.get_archive_subpath())

    assert len(fs.listdir()) == 2
    assert len(fs.listdir('metadata')) == 1

    with fs.open('data/foobar.txt') as fp:
        assert fp.read() == b('test')

    with fs.open('metadata/metadata.csv') as fp:
        assert fp.readline() == 'filename,dc.identifier,dc.identifier\n'
        assert fp.readline() == 'objects/data,1,2\n'
