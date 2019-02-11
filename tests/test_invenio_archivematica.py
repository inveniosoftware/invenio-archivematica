# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask

from invenio_archivematica import InvenioArchivematica
from invenio_archivematica.views.ui import blueprint


def test_version():
    """Test version import."""
    from invenio_archivematica import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioArchivematica(app)
    assert 'invenio-archivematica' in app.extensions

    app = Flask('testapp')
    ext = InvenioArchivematica()
    assert 'invenio-archivematica' not in app.extensions
    ext.init_app(app)
    assert 'invenio-archivematica' in app.extensions


def test_view(app, oauth2):
    """Test view."""
    app.register_blueprint(blueprint)
    with app.test_client() as client:
        res = client.get("/oais/")
        assert res.status_code == 200
        assert 'Welcome to Invenio-Archivematica' in str(res.data)
