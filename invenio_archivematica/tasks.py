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

"""Tasks used by invenio-archivematica."""

from datetime import datetime, timedelta

from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import import_string

from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.signals import oais_transfer_failed, \
    oais_transfer_finished, oais_transfer_processing, oais_transfer_started


@shared_task(ignore_result=True)
def oais_start_transfer(rec_uuid, accessioned_id=''):
    """Archive a record.

    This function should be called to start a transfer to archive a record.
    Once the transfer is finished, you should call
    :py:func:`invenio_archivematica.tasks.archive_record_finish_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_started`
    is called with the record as function parameter.

    :param str rec_uuid: the UUID of the record to archive
    :param str accessioned_id: the AIP accessioned ID. If not given, it will
        not be updated
    """
    # we get the record
    record = Record.get_record(rec_uuid)
    # we register the record as being processed
    ark = Archive.get_from_record(rec_uuid)
    if not ark:
        ark = Archive.create(record.model)
    if accessioned_id:
        ark.aip_accessioned_id = accessioned_id
    ark.status = ArchiveStatus.WAITING
    # we start the transfer
    imp = current_app.config['ARCHIVEMATICA_TRANSFER_FACTORY']
    transfer = import_string(imp)
    transfer(record.id, current_app.config['ARCHIVEMATICA_TRANSFER_FOLDER'])

    db.session.commit()
    oais_transfer_started.send(record)


@shared_task(ignore_result=True)
def oais_process_transfer(rec_uuid, aip_id=None):
    """Mark the transfer in progress.

    This function should be called if the transfer is processing. See
    :py:func:`invenio_archivematica.tasks.archive_record_start_transfer`.

    The signal
    :py:data:`invenio_archivematica.signals.oais_transfer_processing`
    is called with the record as function parameter.

    :param str rec_uuid: the UUID of the record
    :param str aip_id: the ID of the AIP in Archivematica
    """
    ark = Archive.get_from_record(rec_uuid)
    ark.status = ArchiveStatus.PROCESSING
    ark.aip_id = aip_id

    db.session.commit()
    oais_transfer_processing.send(Record(ark.record.json, ark.record))


@shared_task(ignore_result=True)
def oais_finish_transfer(rec_uuid, aip_id):
    """Finalize the transfer of a record.

    This function should be called once the transfer has been finished, to
    mark the record as correctly archived. See
    :py:func:`invenio_archivematica.tasks.archive_record_start_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_finished`
    is called with the record as function parameter.

    :param str rec_uuid: the UUID of the record
    :param str aip_id: the ID in Archivematica of the created AIP
        (should be an UUID)
    """
    ark = Archive.get_from_record(rec_uuid)
    ark.status = ArchiveStatus.REGISTERED
    ark.aip_id = aip_id

    db.session.commit()
    oais_transfer_finished.send(Record(ark.record.json, ark.record))


@shared_task(ignore_result=True)
def oais_fail_transfer(rec_uuid):
    """Mark the transfer as failed.

    This function should be called if the transfer failed. See
    :py:func:`invenio_archivematica.tasks.archive_record_start_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_failed`
    is called with the record as function parameter.

    :param str rec_uuid: the UUID of the record
    """
    ark = Archive.get_from_record(rec_uuid)
    ark.status = ArchiveStatus.FAILED

    db.session.commit()
    oais_transfer_failed.send(Record(ark.record.json, ark.record))


@shared_task(ignore_result=True)
def archive_new_records(days=30, hours=0, minutes=0, seconds=0, delay=True):
    """Start the archive process for some records.

    All the new records that haven't been changed since `nb_days` will be
    archived.

    To trigger this task everyday at 1 am, you can add this variable in your
    config:

    .. code-block:: python

        from celery.schedules import crontab
        # archive all the new records that haven't been modified since 15 days
        CELERYBEAT_SCHEDULE = {
            'archive-records': {
                'task': 'invenio_archivematica.tasks.archive_new_records',
                'schedule': crontab(hour=1),
                'args': [15, 0, 10] # older than 15 days and 10 minutes
            }
        }

    :param int days: number of days that a new record must not have been
        modified to get archived.
    :param int hours: number of hours
    :param int minutes: number of minutes
    :param int seconds: number of seconds
    :param bool delay: tells if we should delay the transfers
    """
    # first we get all the records we need to archive
    begin_date = datetime.now() - timedelta(days=days,
                                            hours=hours,
                                            minutes=minutes,
                                            seconds=seconds)
    arks = Archive.query.join(RecordMetadata).filter(
        Archive.status == ArchiveStatus.NEW,
        RecordMetadata.updated <= str(begin_date)).all()
    # we start the transfer for all the founded records
    for ark in arks:
        if delay:
            oais_start_transfer.delay(ark.record.id)
        else:
            oais_start_transfer(ark.record.id)
