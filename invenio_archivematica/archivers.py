# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Archivers for SIP."""

from __future__ import absolute_import, print_function, unicode_literals

import csv

from flask import current_app
from invenio_sipstore.archivers import BaseArchiver
from six import BytesIO, StringIO
from werkzeug.utils import import_string


class ArchivematicaArchiver(BaseArchiver):
    """Archivematica archiver for SIPs.

    Archives the SIP in the Archivematica archive format.
    """

    def __init__(self, *args, **kwargs):
        """Constructor of the Archiver."""
        kwargs.setdefault('extra_dir', 'metadata')
        kwargs.setdefault('data_dir', 'data')
        super(ArchivematicaArchiver, self).__init__(*args, **kwargs)

    def get_csv_file(self):
        """Create a csv file with generated_metadata."""
        generate_metadata_factory = import_string(current_app.config.get(
            'ARCHIVEMATICA_METADATA_FACTORY'))
        metadata = generate_metadata_factory(self.sip)
        content = StringIO()
        writer = csv.writer(content, delimiter=str(','), lineterminator='\n')
        writer.writerows(zip(*metadata))

        return self._generate_extra_info(content.getvalue(), 'metadata.csv')

    def get_all_files(self):
        """Get the complete list of files in the archive.

        :return: the list of all relative final path
        """
        data_files = self._get_data_files()
        csv_file = self.get_csv_file()
        return data_files + [csv_file]

    def _write_lock_file(self, path):
        """Write a lock file under given path."""
        content = 'this is a lock file - transfer of folder not finished yet'
        fs = self.storage_factory(fileurl=path,
                                  size=len(content),
                                  clean_dir=False)
        fs.save(BytesIO(content.encode('utf-8')))

        return fs

    def _remove_lock_file(self, fs):
        """Remove a lock file."""
        return fs.delete()

    def write_all_files(self):
        """Write all of the archived files to the archivematica file system.

        Creates a temporary 'transfer.lock' file, that will be removed,
        when transfer is done. The lock file prevents archivematica from
        reading a folder, while transfer is still in progress.
        """
        lockfile_path = self.get_fullpath('transfer.lock')

        fs = self._write_lock_file(lockfile_path)
        super(ArchivematicaArchiver, self).write_all_files()
        self._remove_lock_file(fs)
