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

"""Invenio 3 module to connect Invenio to Archivematica."""

ARCHIVEMATICA_BASE_TEMPLATE = 'invenio_archivematica/base.html'
"""Default base template for the demo page."""

ARCHIVEMATICA_TRANSFER_FACTORY = 'invenio_archivematica.factories.transfer'
"""The factory to do the transfers of files to the dashboard.

See :py:func:`invenio_archivematica.factories.transfer_cp`
and :py:data:`invenio_archivematica.config.ARCHIVEMATICA_TRANSFER_FOLDER`
for more information.
"""

ARCHIVEMATICA_ISARCHIVABLE_FACTORY = 'invenio_archivematica.' \
                                     'factories.is_archivable_all'
"""The factory that is used to know if the record should be archived or not.

See :py:func:`invenio_archivematica.factories.is_archivable_all`.
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
