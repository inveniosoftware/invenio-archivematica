# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

"""Invenio 3 module to connect Invenio to Archivematica."""

from __future__ import absolute_import, print_function

from invenio_archivematica.ext import InvenioArchivematica
from invenio_archivematica.version import __version__

__all__ = ('__version__', 'InvenioArchivematica')
