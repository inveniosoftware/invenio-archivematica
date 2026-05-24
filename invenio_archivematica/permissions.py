# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

"""Permissions for archives using Invenio-Archivematica."""

from functools import partial

from invenio_access.permissions import ParameterizedActionNeed

#
# Action needs
#

ArchiveRead = partial(ParameterizedActionNeed, 'archive-read')
"""Action needed: read archive"""

ArchiveWrite = partial(ParameterizedActionNeed, 'archive-write')
"""Action needed: write archive"""

#
# Global action needs
#

archive_read = ArchiveRead(None)
"""Action needed: read all archives."""

archive_write = ArchiveWrite(None)
"""Action needed: write all archives."""


_action2need_map = {
    'archive-read': ArchiveRead,
    'archive-write': ArchiveWrite
}
