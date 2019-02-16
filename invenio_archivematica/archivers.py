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
import json
from datetime import datetime

from flask import current_app
from invenio_db import db
from invenio_sipstore.api import SIP
from invenio_sipstore.archivers import BaseArchiver
from invenio_sipstore.models import RecordSIP, SIPMetadata, SIPMetadataType, \
    current_jsonschemas
from jsonschema import validate
from six import BytesIO, StringIO, b, string_types
from werkzeug.utils import import_string

from .models import Archive


class ArchivematicaArchiver(BaseArchiver):
    """Archivematica archiver for SIPs.

    Archives the SIP in the Archivematica archive format.
    """

    def __init__(self, *args, **kwargs):
        """Constructor of the Archiver."""
        kwargs.setdefault('extra_dir', 'metadata')
        kwargs.setdefault('data_dir', 'data')
        super(ArchivematicaArchiver, self).__init__(*args, **kwargs)

    @staticmethod
    def _generate_metadata(sip):
        """Generate metadata information for Archivematica Archiver.

        This method can bee overwritten in the config variable
        :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FACTORY .

        :return: metadata information for archiver
        :rtype: List[(str,str)]
        """
        metadata = [('filename', 'objects/data')]

        rec_sips = RecordSIP.get_by_sip(sip_id=sip.id)
        metadata.extend(('dc.identifier', str(r.pid_id)) for r in rec_sips)

        return metadata

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
        content = b'this is a lock file - transfer of folder not finished yet'
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
