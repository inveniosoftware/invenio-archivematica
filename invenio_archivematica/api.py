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

"""API for Invenio 3 module to connect Invenio to Archivematica."""

from celery import shared_task
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import import_string

from .models import Archive, ArchiveStatus


def create_accessioned_id(record_pid, pid_type):
    """Create an accessioned ID to store the record in Archivematica.

    :param record_pid: the PID of the record
    :type record_pid: str
    :param pid_type: the type of the PID ('recid'...)
    :type pid_type: str
    :returns: the created ID
    :rtype: str
    """
    resolver = Resolver(pid_type=pid_type, getter=Record.get_record)
    pid, record = resolver.resolve(record_pid)
    return "{service}-{pid_type}-{pid}-{version}".format(
        service=current_app.config['ARCHIVEMATICA_ORGANIZATION_NAME'],
        pid_type=pid_type,
        pid=record_pid,
        version=record.revision_id)


@shared_task(ignore_result=True)
def archive_record_start_transfer(rec_uuid, accessioned_id=None):
    """Archive a record.

    This function should be called to start a transfer to archive a record.
    Once the transfer is finished, you should call
    :py:func:`invenio_archivematica.api.archive_record_finish_transfer`.

    :param rec_uuid: the UUID of the record to archive
    :type rec_uuid: str
    :param accessioned_id: the AIP accessioned ID. If not provided and the
        existing archive object doesn't have any, will be automatically
        computed from
        :py:func:`invenio_archivematica.api.create_accessioned_id`.
    :type accessioned_id: str
    """
    # we get the record
    record = Record.get_record(uuid)
    # we register the record as being processed
    try:
        ark = Archive.query.filter_by(record_id=record.id).one()
    except NoResultFound:
        ark = Archive.create(record.model)
    if not ark.aip_accessioned_id:
        # we compute the accessioned_id
        if not accessioned_id:
            pid = PersistentIdentifier.get_by_object('recid', 'rec', uuid)
            accessioned_id = create_accessioned_id(pid, 'recid')
        ark.aip_accessioned_id = accessioned_id
    ark.status = ArchiveStatus.PROCESSING
    db.session.add(ark)
    # we start the transfer
    imp = current_app.config['ARCHIVEMATICA_TRANSFER_FACTORY']
    transfer = import_string(imp)
    transfer(record.id, current_app.config['ARCHIVEMATICA_TRANSFER_FOLDER'])


@shared_task(ignore_result=True)
def archive_record_finish_transfer(rec_uuid, aip_id):
    """Finalize the transfer of a record.

    This function should be called once the transfer has been finished, to
    mark the record as correctly archived. See
    :py:func:`invenio_archivematica.api.archive_record_start_transfer`.

    :param rec_uuid: the UUID of the record
    :type rec_uuid: str
    :param aip_id: the ID in Archivematica of the created AIP
        (should be an UUID)
    :type aip_id: str
    """
    ark = Archive.query.filter_by(record_id=rec_uuid).one()
    ark.status = ArchiveStatus.REGISTERED
    ark.aip_id = aip_id
    db.session.add(ark)


@shared_task(ignore_result=True)
def archive_record_failed_transfer(rec_uuid):
    """Mark the transfer as failed.

    This function should be called if the transfer failed. See
    :py:func:`invenio_archivematica.api.archive_record_start_transfer`.

    :param rec_uuid: the UUID of the record
    :type rec_uuid: str
    """
    ark = Archive.query.filter_by(record_id=rec_uuid).one()
    ark.status = ArchiveStatus.FAILED
    db.session.add(ark)
