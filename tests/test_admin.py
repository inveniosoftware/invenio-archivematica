# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test the admin view."""

from flask_admin import Admin, menu

from invenio_archivematica.admin import archive_adminview


def test_admin(app, db):
    """Test the flask-admin interfarce."""
    admin = Admin(app, name='AdminExt')

    # register models in admin
    assert 'model' in archive_adminview
    assert 'modelview' in archive_adminview
    admin_kwargs = dict(archive_adminview)
    model = admin_kwargs.pop('model')
    modelview = admin_kwargs.pop('modelview')
    admin.add_view(modelview(model, db.session, **admin_kwargs))

    # Check if generated admin menu contains the correct items
    menu_items = {str(item.name): item for item in admin.menu()}

    # Records should be a category
    assert 'Records' in menu_items
    assert menu_items['Records'].is_category()
    assert isinstance(menu_items['Records'], menu.MenuCategory)

    # Archive menu should be a modelview
    submenu_items = {str(item.name): item for item in
                     menu_items['Records'].get_children()}
    assert 'Archive' in submenu_items
    assert isinstance(submenu_items['Archive'], menu.MenuView)
