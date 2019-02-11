# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OAuth2 scopes for Invenio-Archivematica."""

from flask_babelex import lazy_gettext as _
from invenio_oauth2server.models import Scope


class ArchiveScope(Scope):
    """Basic deposit scope."""

    def __init__(self, id_, *args, **kwargs):
        """Define the scope."""
        super(ArchiveScope, self).__init__(
            id_='archive:{0}'.format(id_),
            group='deposit', *args, **kwargs
        )


archive_scope = ArchiveScope(
    'actions',
    help_text=_('Allow to view, edit and download Archives.'))
"""Allow to view, edit and download Archives."""
