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

"""Invenio 3 module to connect Invenio to Archivematica"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'invenio-accounts>=1.0.0b9',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.3',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1,<1.6',  # TODO unpin see https://github.com/inveniosoftware/troubleshooting/issues/11
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=2.4.0',
    'pytest-runner>=2.11.1',
]

install_requires = [
    'Flask-BabelEx>=0.9.3',
    'Flask-CeleryExt>=0.3.0',
    'alembic>=0.9.3',
    'invenio-admin>=1.0.0b4',
    'invenio-access>=1.0.0b1',
    'invenio-db>=1.0.0b8',
    'invenio-files-rest>=1.0.0a19',
    'invenio-oauth2server>=1.0.0b1',
    'invenio-rest[cors]>=1.0.0b1',
    'invenio-sipstore>=1.0.0a7'
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_archivematica', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-archivematica',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='GPLv2',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/remileduc/invenio-archivematica',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.api_apps': [
            'invenio_archivematica = invenio_archivematica:InvenioArchivematica',
        ],
        'invenio_base.apps': [
            'invenio_archivematica = invenio_archivematica:InvenioArchivematica',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_archivematica',
        ],
        # TODO: Edit these entry points to fit your needs.
        'invenio_access.actions': [
            'archive_read = invenio_archivematica.permissions:archive_read',
            'archive_write = invenio_archivematica.permissions:archive_write',
        ],
        # 'invenio_admin.actions': [],
        'invenio_admin.views': [
            'invenio_archivematica_archive = '
            'invenio_archivematica.admin:archive_adminview',
        ],
        # 'invenio_assets.bundles': [],
        # 'invenio_base.api_apps': [],
        'invenio_base.api_blueprints': [
            'invenio_archivematica = invenio_archivematica.views.rest:blueprint',
        ],
        'invenio_base.blueprints': [
            'invenio_archivematica = invenio_archivematica.views.ui:blueprint',
        ],
        'invenio_celery.tasks': [
            'invenio_archivematica = invenio_archivematica.tasks'
        ],
        # 'invenio_db.models': [],
        # 'invenio_pidstore.minters': [],
        # 'invenio_records.jsonresolver': [],
        'invenio_oauth2server.scopes': [
            'archivematica_archive = invenio_archivematica.scopes:archive_scope'
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
