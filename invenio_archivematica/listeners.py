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

"""Listeners connected to signals."""

from flask import current_app
from werkzeug.utils import import_string

from invenio_archivematica.models import Archive, ArchiveStatus


def listener_sip_created(sip, *args, **kwargs):
    """Create an entry in the database when a sip is created."""
    imp = current_app.config['ARCHIVEMATICA_ISARCHIVABLE_FACTORY']
    is_archivable = import_string(imp) if imp else None
    ark = Archive.create(sip.model)
    if not is_archivable or not is_archivable(sip):
        ark.status = ArchiveStatus.IGNORED
