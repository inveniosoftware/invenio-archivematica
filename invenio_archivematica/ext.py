# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio 3 module to connect Invenio to Archivematica."""

from invenio_sipstore.signals import sipstore_created

from . import config
from .listeners import listener_sip_created


class InvenioArchivematica(object):
    """Invenio-Archivematica extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)
            self.init_listeners()

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-archivematica'] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        if 'BASE_TEMPLATE' in app.config:
            app.config.setdefault(
                'ARCHIVEMATICA_BASE_TEMPLATE',
                app.config['BASE_TEMPLATE'],
            )
        for k in dir(config):
            if k.startswith('ARCHIVEMATICA_'):
                app.config.setdefault(k, getattr(config, k))

    def init_listeners(self):
        """Register the listener to invenio_sipstore's signals."""
        sipstore_created.connect(listener_sip_created)
