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
from invenio_sipstore.api import SIP
from werkzeug.utils import import_string

from invenio_archivematica.models import Archive, ArchiveStatus
from invenio_archivematica.signals import oais_transfer_failed, \
    oais_transfer_finished, oais_transfer_processing, oais_transfer_started


@shared_task(ignore_result=True)
def oais_start_transfer(uuid, accession_id='', archivematica_id=None):
    """Archive a sip.

    This function should be called to start a transfer to archive a sip.
    Once the transfer is finished, you should call
    :py:func:`invenio_archivematica.tasks.oais_finish_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_started`
    is called with the sip as function parameter.

    :param str uuid: the UUID of the sip to archive
    :param str accession_id: the AIP accession ID. You can generate one from
    :py:func:`invenio_archivematica.factories.create_accession_id`
    """
    # we get the sip
    sip = SIP.get_sip(uuid)
    # we register the sip as being processed
    ark = Archive.get_from_sip(uuid)
    if not ark:
        ark = Archive.create(sip.model)
    ark.accession_id = accession_id
    ark.status = ArchiveStatus.WAITING
    # we start the transfer
    imp = current_app.config['ARCHIVEMATICA_TRANSFER_FACTORY']
    transfer = import_string(imp)
    ret = transfer(sip.id, current_app.config['ARCHIVEMATICA_TRANSFER_FOLDER'])
    if ret == 0:
        db.session.commit()
        oais_transfer_started.send(sip)
        return
    oais_fail_transfer(uuid, accession_id)


@shared_task(ignore_result=True)
def oais_process_transfer(uuid, accession_id='', archivematica_id=None):
    """Mark the transfer in progress.

    This function should be called if the transfer is processing. See
    :py:func:`invenio_archivematica.tasks.oais_start_transfer`.

    The signal
    :py:data:`invenio_archivematica.signals.oais_transfer_processing`
    is called with the sip as function parameter.

    :param str uuid: the UUID of the sip
    :param str archivematica_id: the ID of the AIP in Archivematica
    """
    ark = Archive.get_from_sip(uuid)
    ark.status = ArchiveStatus.PROCESSING_TRANSFER
    ark.archivematica_id = archivematica_id

    db.session.commit()
    oais_transfer_processing.send(SIP(ark.sip))


@shared_task(ignore_result=True)
def oais_process_aip(uuid, accession_id='', archivematica_id=None):
    """Mark the aip in progress.

    This function should be called if the aip is processing. See
    :py:func:`invenio_archivematica.tasks.oais_start_transfer`.

    The signal
    :py:data:`invenio_archivematica.signals.oais_transfer_processing`
    is called with the sip as function parameter.

    :param str uuid: the UUID of the sip
    :param str archivematica_id: the ID of the AIP in Archivematica
    """
    ark = Archive.get_from_sip(uuid)
    ark.status = ArchiveStatus.PROCESSING_AIP
    ark.archivematica_id = archivematica_id

    db.session.commit()
    oais_transfer_processing.send(SIP(ark.sip))


@shared_task(ignore_result=True)
def oais_finish_transfer(uuid, accession_id='', archivematica_id=None):
    """Finalize the transfer of a sip.

    This function should be called once the transfer has been finished, to
    mark the sip as correctly archived. See
    :py:func:`invenio_archivematica.tasks.oais_start_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_finished`
    is called with the sip as function parameter.

    :param str uuid: the UUID of the sip
    :param str archivematica_id: the ID in Archivematica of the created AIP
        (should be an UUID)
    """
    ark = Archive.get_from_sip(uuid)
    ark.status = ArchiveStatus.REGISTERED
    ark.archivematica_id = archivematica_id
    ark.sip.archived = True

    db.session.commit()
    oais_transfer_finished.send(SIP(ark.sip))


@shared_task(ignore_result=True)
def oais_fail_transfer(uuid, accession_id='', archivematica_id=None):
    """Mark the transfer as failed.

    This function should be called if the transfer failed. See
    :py:func:`invenio_archivematica.tasks.oais_start_transfer`.

    The signal :py:data:`invenio_archivematica.signals.oais_transfer_failed`
    is called with the sip as function parameter.

    :param str uuid: the UUID of the sip
    """
    ark = Archive.get_from_sip(uuid)
    ark.status = ArchiveStatus.FAILED
    ark.sip.archived = False

    db.session.commit()
    oais_transfer_failed.send(SIP(ark.sip))


@shared_task(ignore_result=True)
def archive_new_sips(accession_id_factory, days=30, hours=0, minutes=0,
                     seconds=0, delay=True):
    """Start the archive process for some sip.

    All the new sip that have been created at least since `nb_days` will be
    archived.

    To trigger this task everyday at 1 am, you can add this variable in your
    config:

    .. code-block:: python

        from celery.schedules import crontab
        # archive all the new sip that haven't been modified since 15 minutes
        CELERYBEAT_SCHEDULE = {
            'archive-sips': {
                'task': 'invenio_archivematica.tasks.archive_new_sips',
                'schedule': crontab(hour=1),
                'kwargs': {
                    'accession_id_factory':
                        'invenio_archivematica.factories.create_accession_id',
                    'days': 0,
                    'hours': 0,
                    'minutes': 15, # sip older than 15 minutes
                    'seconds': 0,
                    'delay': True
                }
            }
        }

    :param str accession_id_factory: the path to the factory to create the
        accession_id of the archive. See
        :py:func:`invenio_archivematica.factories.create_accession_id`. The
        archive is sent to the function.
    :param int days: number of days that a new sip must not have been
        modified to get archived.
    :param int hours: number of hours
    :param int minutes: number of minutes
    :param int seconds: number of seconds
    :param bool delay: tells if we should delay the transfers
    """
    # first we get all the sip we need to archive
    begin_date = datetime.utcnow() - timedelta(days=days,
                                               hours=hours,
                                               minutes=minutes,
                                               seconds=seconds)
    arks = Archive.query.filter(
        Archive.status == ArchiveStatus.NEW,
        Archive.updated <= str(begin_date)).all()
    facto = import_string(accession_id_factory)
    # we start the transfer for all the founded sip
    for ark in arks:
        accession_id = facto(ark)
        if delay:
            oais_start_transfer.delay(ark.sip.id, accession_id)
        else:
            oais_start_transfer(ark.sip.id, accession_id)
