# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test archiver."""

from six import b

from invenio_archivematica.archivers import ArchivematicaArchiver


def test_write_all_files(app, db, archive_fs, sip):
    """Test saving files by Archivematica Archiver."""

    archiver = ArchivematicaArchiver(sip)

    assert not archive_fs.listdir()

    archiver.write_all_files()
    fs = archive_fs.opendir(archiver.get_archive_subpath())

    assert len(fs.listdir()) == 2
    assert len(fs.listdir('metadata')) == 1

    with fs.open('data/foobar.txt') as fp:
        assert fp.read() == 'test'

    with fs.open('metadata/metadata.csv') as fp:
        assert fp.readline() == 'filename,dc.identifier,dc.identifier\n'
        assert fp.readline() == 'objects/data,1,2\n'
