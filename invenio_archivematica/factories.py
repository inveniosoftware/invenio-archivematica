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

from flask import current_app
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
    :param config: can be empty. It will have the content of the variable
        :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`.
        However, it will use the export folder set in
        :py:data:`invenio_sipstore.config.SIPSTORE_ARCHIVER_LOCATION_NAME`
    """
    sip = SIP.get_sip(uuid)
    archiver = BaseArchiver(sip)
    archiver.write_all_files()
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
    sip = SIP.get_sip(uuid)

    # first we copy everything in a temp folder
    archiver = BaseArchiver(sip)
    archiver.write_all_files()

    # then we rsync to the final dest
    src_path = archiver.get_fullpath('')
    dest_path = config['destination']
    if config.get('server', None) and config.get('user', None):
        dest_path = '{user}@{server}:{dest}'.format(user=config['user'],
                                                    server=config['server'],
                                                    dest=dest_path)
    try:
        ret = call(['rsync',
                    config['args'],
                    src_path,
                    dest_path])
    # we remove the temp folder
    finally:
        rmtree(src_path)
    return ret


def transfer_demo(uuid, config):
    """Transfer the files contained in the sip to the destination.

    Very similar to the rsync transfer. However, because of time, I use the
    VERY UNSECURE sshpass package for rsync authentication.
    DO NOT USE IN PROD!!!

    :param str uuid: the id of the sip containing files to transfer
    :param dict config: here config must be a dict with the following keys:
        - user - the SSH user
        - password_file - a path where the password is stored
        - remote - the URL or IP of the remote
        - remote_path - where to store files on the remote
        - args - the args for rsync
    """
    # we retrieve the archive and the SIP associated
    sip = SIP.get_sip(uuid)
    ark = Archive.get_from_sip(uuid)

    # we export it to the temp folder
    archiver = BaseArchiver(sip)
    archiver.write_all_files()

    # we rsync it to the remote
    src_path = archiver.get_fullpath('')
    dest_path = join(config['remote_path'], ark.accession_id)
    dest_path = '{}:{}'.format(config['remote'], dest_path)
    ssh_command = 'sshpass -f {filename} ssh -l {user}'.format(
        filename=config['password_file'],
        user=config['user'])
    return call(['rsync',
                 config['args'],
                 '--rsh={}'.format(ssh_command),
                 src_path,
                 dest_path])


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
