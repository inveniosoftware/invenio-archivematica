# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
