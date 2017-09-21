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

"""Script to create an archive object from 0 into Invenio.

This script can be copy / paste in the invenio shell: run ``invenio shell``
to access it.
"""

import uuid
from os import makedirs

from invenio_db import db
from invenio_files_rest.models import Bucket, Location
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record, RecordsBuckets
from invenio_sipstore.api import RecordSIP
from invenio_sipstore.models import SIPMetadataType
from six import BytesIO

from invenio_archivematica.tasks import oais_start_transfer

# init
try:
    makedirs('/archive/')
except:
    pass
locrecords = Location(
    name='records',
    uri='/eos/workspace/o/oais/archivematica-test/records/',
    default=True
)
locarchive = Location(
    name='archive',  # this should go in SIPSTORE_ARCHIVER_LOCATION_NAME
    uri='/eos/workspace/o/oais/archivematica-test/transfer/'
)
db.session.add(locrecords)
db.session.add(locarchive)
db.session.commit()

# first we create a metadata type with a schema used by the following record
mtype = SIPMetadataType(title='Invenio JSON test',
                        name='invenio-json-test',
                        format='json',
                        schema='https://zenodo.org/schemas/deposits/records/record-v1.0.0.json')
db.session.add(mtype)
db.session.commit()

# create record, it needs to use the same schema as the one in the metadata type
recid = uuid.uuid4()
pid = PersistentIdentifier.create('recid', '1501', object_type='rec',
                                  object_uuid=recid,
                                  status=PIDStatus.REGISTERED)
record = Record.create({'$schema': 'https://zenodo.org/schemas/deposits/records/record-v1.0.0.json',
                        '_deposit': {'status': 'draft'},
                        'title': 'demo'},
                       recid)
record.commit()
db.session.commit()

# put a file in the record
stream = BytesIO(b'head crab\n')
b = Bucket.create()
RecordsBuckets.create(bucket=b, record=record.model)
db.session.commit()
record.files['crab.txt'] = stream
record.files.dumps()
record.commit()
db.session.commit()

# create the archive
sip = RecordSIP.create(pid, record, True, user_id=1, agent={'demo': 'archivematica'})
db.session.commit()

# archive it
oais_start_transfer(sip.sip.id, 'test-demo-archivematica')
