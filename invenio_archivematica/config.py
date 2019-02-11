# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio 3 module to connect Invenio to Archivematica."""

ARCHIVEMATICA_BASE_TEMPLATE = 'invenio_archivematica/base.html'
"""Default base template for the demo page."""

ARCHIVEMATICA_TRANSFER_FACTORY = 'invenio_archivematica.factories.transfer_cp'
"""The factory to do the transfers of files to the dashboard.

See :py:func:`invenio_archivematica.factories.transfer_cp`
and :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`
for more information.
"""

ARCHIVEMATICA_ISARCHIVABLE_FACTORY = 'invenio_archivematica.' \
                                     'factories.is_archivable_default'
"""The factory that is used to know if the sip should be archived or not.

See :py:func:`invenio_archivematica.factories.is_archivable_default`.
"""

ARCHIVEMATICA_ORGANIZATION_NAME = 'CERN'
"""Organization name setup in Archivematica's dashboard."""

ARCHIVEMATICA_TRANSFER_FOLDER = '.'
"""The transfer folder setup in the dashboard.

If you use a custom factory to do the transfer, you can put whatever you want
here, it will be passed to your factory. See
:py:func:`invenio_archivematica.factories.transfer_cp` and
:py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FACTORY`.
"""

ARCHIVEMATICA_DASHBOARD_URL = 'http://localhost:81'
"""The URL to Archivematica Dashboard."""

ARCHIVEMATICA_DASHBOARD_USER = 'invenio'
"""The user to connect to Archivematica Dashboard."""

ARCHIVEMATICA_DASHBOARD_API_KEY = 'change me'
"""The API key to use with the user above."""

ARCHIVEMATICA_STORAGE_URL = 'http://localhost:8001'
"""The URL to Archivematica Storage."""

ARCHIVEMATICA_STORAGE_USER = 'invenio'
"""The user to connect to Archivematica Storage."""

ARCHIVEMATICA_STORAGE_API_KEY = 'change me'
"""The API key to use with the user above."""
