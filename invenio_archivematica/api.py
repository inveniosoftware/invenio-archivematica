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

from invenio_archivematica.models import ArchiveStatus
from invenio_archivematica.tasks import oais_fail_transfer, \
    oais_finish_transfer, oais_process_transfer, oais_start_transfer


def start_transfer(sip, accession_id, archivematica_id=None):
    """Start the archive process for a sip.

    Start the transfer of the sip in asynchronous mode. See
    :py:mod:`invenio_archivematica.tasks`

    :param sip: the sip to archive
    :type sip: :py:class:`invenio_sipstore.api.SIP`
    :param str accession_id: the accessioned ID in archivematica. You can
        compute it from
        :py:func:`invenio_archivematica.factories.create_accession_id`
    :param str archivematica_id: the ID in Archivematica
    """
    oais_start_transfer.delay(str(sip.id), accession_id, archivematica_id)


def process_transfer(sip, accession_id='', archivematica_id=None):
    """Create the archive for a sip.

    Process the transfer of the sip in asynchronous mode. See
    :py:mod:`invenio_archivematica.tasks`

    :param sip: the sip to archive
    :type sip: :py:class:`invenio_sipstore.api.SIP`
    :param str accession_id: the accession_id
    :param str archivematica_id: the ID of the AIP in Archivematica
    """
    oais_process_transfer(str(sip.id), accession_id, archivematica_id)


def process_aip(sip, accession_id='', archivematica_id=None):
    """Create the archive for a sip.

    Process the aip of the sip in asynchronous mode. See
    :py:mod:`invenio_archivematica.tasks`

    :param sip: the sip to archive
    :type sip: :py:class:`invenio_sipstore.api.SIP`
    :param str accession_id: the accession_id
    :param str archivematica_id: the ID of the AIP in Archivematica
    """
    oais_process_aip(str(sip.id), accession_id, archivematica_id)


def finish_transfer(sip, accession_id='', archivematica_id=None):
    """Finish the archive process for a sip.

    Finish the transfer of the sip in asynchronous mode. See
    :py:mod:`invenio_archivematica.tasks`

    :param sip: the sip to archive
    :type sip: :py:class:`invenio_sipstore.api.SIP`
    :param str accession_id: the accession_id
    :param str archivematica_id: the ID of the created AIP in Archivematica
    """
    oais_finish_transfer(str(sip.id), accession_id, archivematica_id)


def fail_transfer(sip, accession_id='', archivematica_id=None):
    """Fail the archive process for a sip.

    Fail the transfer of the sip in asynchronous mode. See
    :py:mod:`invenio_archivematica.tasks`

    :param sip: the sip to archive
    :type sip: :py:class:`invenio_sipstore.api.SIP`
    :param str accession_id: the accession_id
    :param str archivematica_id: the ID of the created AIP in Archivematica
    """
    oais_fail_transfer(str(sip.id), accession_id, archivematica_id)


change_status_func = {
    ArchiveStatus.NEW: start_transfer,
    ArchiveStatus.WAITING: start_transfer,
    ArchiveStatus.PROCESSING_TRANSFER: process_transfer,
    ArchiveStatus.PROCESSING_AIP: process_aip,
    ArchiveStatus.REGISTERED: finish_transfer,
    ArchiveStatus.FAILED: fail_transfer,
    ArchiveStatus.IGNORED: None,
    ArchiveStatus.DELETED: None
}
"""Dictionary that maps status to functions used to change the status."""
