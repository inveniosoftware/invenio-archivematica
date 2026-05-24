# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

"""Test helpers."""


def archive_directory_builder(sip):
    """Build a directory for the archived SIP."""
    return ['test']


def transfer_fail(*args, **kwargs):
    """Return 1, as if a transfer had failed."""
    return 1
