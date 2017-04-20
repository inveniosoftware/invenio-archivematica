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

"""Factories used to customize the behavior of the module."""

from json import dumps
from os import mkdir
from os.path import join
from shutil import copyfile

from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record

from .api import create_accessioned_id


def transfer_cp(uuid, destination):
    """Transfer the files contained in the record to the destination.

    This method is automatically called by the module to transfer the files.
    Depending on your installation, you may want to have a different behavior
    (copy among servers...). Then, you can create your own factory and link it
    into the config variable
    :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FACTORY`.

    :param uuid: the id of the record containing files to transfer
    :param destination: the destination folder - this will be what is
        inside the config variable
        :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`.
        It needs to be a absolute path to a folder
    """
    record = Record.get_record(uuid)
    pid = PersistentIdentifier.get_by_object('recid', 'rec', uuid)
    dir_name = join(destination,
                    create_accessioned_id(pid.pid_value, 'recid'))
    try:
        mkdir(dir_name)
    except OSError:
        pass
    for fileobj in record.files:
        copyfile(fileobj.file.storage().fileurl,
                 join(dir_name, fileobj.key))

<<<<<<< HEAD
def is_archivable(record):
=======

def is_archivable_all(record):
>>>>>>> API: functions to archive a record
    """Tell if the given record should be archived or not.

    If this function returns True, the record will be archived later.
    Otherwise, the record will never get archived.

    This function archive all the records.
    """
    return True


def is_archivable_none(record):
    """Archive no records."""
    return False
