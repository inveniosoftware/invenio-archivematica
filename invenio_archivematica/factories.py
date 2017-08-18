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

from os.path import join
from shutil import rmtree
from subprocess import call
from tempfile import mkdtemp

from flask import current_app
from fs.opener import opener
from invenio_sipstore.api import SIP
from invenio_sipstore.archivers import BaseArchiver

from invenio_archivematica.models import Archive


def create_accession_id(ark):
    """Create an accession ID to store the sip in Archivematica.

    :param ark: the archive
    :type ark: :py:class:`invenio_archivematica.models.Archive`
    :returns: the created ID: SERVICE-SIP_UUID
    :rtype: str
    """
    return "{service}-{uuid}".format(
        service=current_app.config['ARCHIVEMATICA_ORGANIZATION_NAME'],
        uuid=ark.sip.id)


def transfer_cp(uuid, config):
    """Transfer the files contained in the sip to a local destination.

    The transfer is done with a simple copy of files.

    This method is automatically called by the module to transfer the files.
    Depending on your installation, you may want to have a different behavior
    (copy among servers...). Then, you can create your own factory and link it
    into the config variable
    :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FACTORY`.

    :param str uuid: the id of the sip containing files to transfer
    :param config: the destination folder - this will be what is
        inside the config variable
        :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`.
        It needs to be a absolute path to a folder
    """
    sip = SIP.get_sip(uuid)
    ark = Archive.get_from_sip(uuid)
    archiver = BaseArchiver(sip)
    fs, path = opener.parse(config, writeable=True, create_dir=True)
    fs = fs.opendir(path)
    archiver.init(fs, ark.accession_id)
    archiver.create()
    return 0


def transfer_rsync(uuid, config):
    """Transfer the files contained in the sip to the destination.

    The transfer is done with a rsync. If transfer to remote, you need a valid
    ssh setup.

    This method is automatically called by the module to transfer the files.
    Depending on your installation, you may want to have a different behavior
    (copy among servers...). Then, you can create your own factory and link it
    into the config variable
    :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FACTORY`.

    The config needs to include at least the destination folder. If transfer
    to remote, it needs to include the user and the server. In either cases,
    you can include usual rsync parameters. See
    :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`:

    .. code-block:: python

        ARCHIVEMATICA_TRANSFER_FOLDER = {
            'server': 'localhost',
            'user': 'invenio',
            'destination': '/tmp',
            'args': '-az'
        }

    :param str uuid: the id of the sip containing files to transfer
    :param config: the config for rsync
    """
    ark = Archive.get_from_sip(uuid)

    # first we copy everything in a temp folder
    ftmp = mkdtemp()
    transfer_cp(uuid, ftmp)
    # then we rsync to the final dest
    try:
        rectmp = join(ftmp, ark.accession_id)
        if 'server' in config and 'user' in config:
            fdest = '{user}@{server}:{dest}'.format(user=config['user'],
                                                    server=config['server'],
                                                    dest=config['destination'])
        else:
            fdest = config['destination']
        ret = call(['rsync',
                    config['args'],
                    rectmp,
                    fdest])
    # we remove the temp folder
    finally:
        rmtree(ftmp)
    return ret


def is_archivable_default(sip):
    """Tell if the given sip should be archived or not.

    If this function returns True, the sip will be archived later.
    Otherwise, the sip will never get archived.

    This function returns the archived flag on the SIP.
    """
    return sip.archivable


def is_archivable_none(sip):
    """Archive no sip."""
    return False
