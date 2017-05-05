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

"""Signals for the module."""

from blinker import Namespace

_signals = Namespace()

oais_transfer_started = _signals.signal('oais_transfer_started')
"""Signal sent each time a record has been transfered.

Send the record as a parameter: :py:class:`invenio_records.api.Record`

Example subscriber

.. code-block:: python

    from invenio_archivematica.models import Archive, ArchiveStatus
    def listener(sender, *args, **kwargs):
        # sender is the record being archived
        ark = Archive.get_from_record(sender.id)
        assert ark.status == ArchiveStatus.PROCESSING

    from invenio_archivematica.signals import oais_transfer_started
    oais_transfer_started.connect(listener)
"""

oais_transfer_processing = _signals.signal('oais_transfer_finished')
"""Signal sent when a transfered record is being processed."""

oais_transfer_finished = _signals.signal('oais_transfer_finished')
"""Signal sent when a transfer has finished."""

oais_transfer_failed = _signals.signal('oais_transfer_failed')
"""Signal sent when a transfer has failed."""
