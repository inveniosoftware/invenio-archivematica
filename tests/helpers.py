
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test helpers."""


def archive_directory_builder(sip):
    """Build a directory for the archived SIP."""
    return ['test']


def transfer_fail(*args, **kwargs):
    """Return 1, as if a transfer had failed."""
    return 1
