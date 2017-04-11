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

from flask import current_app

from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


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
