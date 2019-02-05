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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB
from invenio_db import db as db_
from invenio_files_rest import InvenioFilesREST
from invenio_files_rest.models import Location
from invenio_oauth2server import InvenioOAuth2Server, InvenioOAuth2ServerREST
from invenio_oauth2server.views import server_blueprint
from invenio_rest import InvenioREST
from invenio_sipstore import InvenioSIPStore
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_archivematica import InvenioArchivematica
from invenio_archivematica.views.rest import blueprint


@pytest.yield_fixture()
def instance_path():
    """Temporary instance path."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.fixture()
def base_app(instance_path):
    """Flask application fixture."""
    app_ = Flask('testapp', instance_path=instance_path)
    app_.config.update(
        OAUTH2_CACHE_TYPE='simple',
        OAUTHLIB_INSECURE_TRANSPORT=True,
        SECRET_KEY='SECRET_KEY',
        SERVER_NAME='invenio.org',
        SIPSTORE_AGENT_JSONSCHEMA_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                               'sqlite:///test.db'),
        TESTING=True,
    )
    Babel(app_)
    InvenioArchivematica(app_)
    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask full application fixture."""
    Breadcrumbs(base_app)
    InvenioDB(base_app)
    InvenioAccess(base_app)
    InvenioAccounts(base_app)
    InvenioFilesREST(base_app)
    InvenioOAuth2Server(base_app)
    InvenioOAuth2ServerREST(base_app)
    InvenioREST(base_app)
    InvenioSIPStore(base_app)
    base_app.register_blueprint(server_blueprint)
    base_app.register_blueprint(blueprint)
    with base_app.app_context():
        yield base_app


@pytest.yield_fixture()
def db(app):
    """Flask database fixture."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()
    drop_database(str(db_.engine.url))


@pytest.yield_fixture()
def location(app, db):
    """Define a location to write SIPs with factories."""
    path = os.path.abspath('./tmp/')
    try:
        os.mkdir(path)
    except:
        pass
    loc = Location(name='archive', uri=path, default=True)
    db.session.add(loc)
    db.session.commit()
    app.config['SIPSTORE_ARCHIVER_LOCATION_NAME'] = 'archive'
    yield loc
    shutil.rmtree(path)


@pytest.yield_fixture()
def client(app):
    """Flask client fixture."""
    with app.test_client() as client:
        yield client


@pytest.fixture()
def oauth2(app, db):
    """Creates authentication tokens for test.

    Add these attributes in the app object and return app:
    - user: a fake user that have authorization to archive_read and write
    - token: api token for user
    """
    from invenio_access.models import ActionUsers
    from invenio_oauth2server.models import Token

    from invenio_archivematica.permissions import archive_read, archive_write

    datastore = app.extensions['security'].datastore
    app.user = datastore.create_user(
        email='info@inveniosoftware.org', password='tester',
        active=True)
    db.session.commit()
    db.session.add(ActionUsers.allow(archive_read, user=app.user))
    db.session.add(ActionUsers.allow(archive_write, user=app.user))
    app.token = Token.create_personal(
        'test-', app.user.id, scopes=['archive:actions'], is_internal=True
    ).access_token
    db.session.commit()

    return app
