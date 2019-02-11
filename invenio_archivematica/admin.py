# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Admin views fot the table Archive."""

from flask_admin.contrib.sqla import ModelView

from invenio_archivematica.models import Archive


class ArchiveModelView(ModelView):
    """ModelView for the Archive table."""

    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_display_all_relations = True
    column_list = (
        'sip_id', 'sip.created', 'status', 'accession_id', 'archivematica_id'
    )
    column_labels = {
        'sip_id': 'ID of the SIP',
        'sip.created': 'Last update',
        'status': 'Status',
        'accession_id': 'AIP Accession ID',
        'archivematica_id': 'Archivematica ID'
    }
    page_size = 25


archive_adminview = dict(
    modelview=ArchiveModelView,
    model=Archive,
    name='Archive',
    category='Records')
