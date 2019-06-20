# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio 3 module to connect Invenio to Archivematica."""

from __future__ import absolute_import, print_function

from invenio_archivematica.ext import InvenioArchivematica
from invenio_archivematica.version import __version__

__all__ = ('__version__', 'InvenioArchivematica')
