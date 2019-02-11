# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Signals for the module."""

from blinker import Namespace

_signals = Namespace()

oais_transfer_started = _signals.signal('oais_transfer_started')
"""Signal sent each time a sip has been transfered.

Send the sip as a parameter: :py:class:`invenio_sipstore.api.SIP`

Example subscriber

.. code-block:: python

    from invenio_archivematica.models import Archive, ArchiveStatus
    def listener(sender, *args, **kwargs):
        # sender is the sip being archived
        ark = Archive.get_from_sip(sender.id)
        assert ark.status == ArchiveStatus.PROCESSING

    from invenio_archivematica.signals import oais_transfer_started
    oais_transfer_started.connect(listener)
"""

oais_transfer_processing = _signals.signal('oais_transfer_finished')
"""Signal sent when a transfered sip is being processed."""

oais_transfer_finished = _signals.signal('oais_transfer_finished')
"""Signal sent when a transfer has finished."""

oais_transfer_failed = _signals.signal('oais_transfer_failed')
"""Signal sent when a transfer has failed."""
