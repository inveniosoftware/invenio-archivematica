..
    This file is part of Invenio.
    Copyright (C) 2017-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Usage
=====

Instructions for using Invenio-Archivematica to archive a file. This documents
assumes that you have Invenio, Invenio-Archivematica, Archivematica and the
automation-tools installed. For more info please checkout the
`installation instructions <installation.rst>`_.

.. contents::

Concepts
========
This is how the Invenio to Archivematica workflow works:

1. On Invenio, you create a Submission Information Package (SIP) that contains
   everything you want to archive. Typically a SIP is a collection of files and
   metadata. You can see your SIPs in the Invenio admin menu: ``/admin/sip/``.

2. Invenio will automatically create an archive object with the status ``NEW``
   You can see the Archive object in the Invenio admin menu:``/admin/archive/``.

3. The next step is to let Invenio start the transfer to Archivematica. The
   Archive is updated with the status ``WAITING`` and the files and metadata are
   copied to the transfer folder of Archivematica waiting for processing.

4. Each time the automation-tool run Archivematica checks the status of the
   active transfer and notifies Invenio about the process. If there are no
   active transfers Archivematica checks the transfer folder for new files and
   starts processing.

5. When the transfer is succesfull the files are stored in the storage inside
   an AIP.

Archiving a record
==================
In this section we will describe in detail how a record is archived. For this,
we will follow `create_archive.py
<https://github.com/inveniosoftware/invenio-archivematica/blob/master/examples/create_archive.py>`_
step by step.

Initialization
--------------
On the web container, run the Invenio shell. Note that you need to able to
import all requirements for the script to function properly.

.. code:: python

   import uuid
   from os import makedirs

   from six import BytesIO

   from invenio_archivematica.tasks import oais_start_transfer
   from invenio_db import db
   from invenio_files_rest.models import Bucket, Location
   from invenio_pidstore.models import PersistentIdentifier, PIDStatus
   from invenio_records_files.api import Record, RecordsBuckets
   from invenio_sipstore.api import RecordSIP
   from invenio_sipstore.models import SIPMetadataType

First we need to set the locations for the SIP records and the Archive objects.
For the development setup this would default to:

.. code:: python

    try:
        makedirs('/archive/')
    except:
        pass
    locrecords = Location(
        name='records',
        # Insert here the directory where you want your records to go
        uri='/home/{username}/invenio-records',
        default=True
    )
    locarchive = Location(
        # This should go in SIPSTORE_ARCHIVER_LOCATION_NAME
        name='archive',
        # Insert here the directory shared with archivematica
        uri='/home/jorik/.am/ss-location-data'
    )
    db.session.add(locrecords)
    db.session.add(locarchive)
    db.session.commit()

The first location, ``locrecords``, is the one where the records are saved.
Records in this folder are not yet shipped to Archivematica. Once they appear in
the second location, ``locarchive``, they are in the transfer folder and can be
ingested by Archivematica. *Note*: the name of the archive location *needs* to
be the same as the name put in the variable ``SIPSTORE_ARCHIVER_LOCATION_NAME``.

Next we create a metadata type. Here, the name of the metadata type *must*
appear in the config variable ``SIPSTORE_ARCHIVER_METADATA_TYPES``. This schema
will be used when creating SIP records:

.. code:: python

   mtype = SIPMetadataType(title='Invenio JSON test',
                           name='invenio-json-test',
                           format='json',
                           schema='https://zenodo.org/schemas/deposits/records/record-v1.0.0.json')
   db.session.add(mtype)
   db.session.commit()

Create a SIP
------------
The basis for al archival operations is the SIP. The SIP contains all the files
that need to be archived, plus the metadata for these files. But before we can
create a SIP we need to create a dummy record in Invenio containing a file:

.. code:: python

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

The schema of the new record must be the same as the schema that is used for
the ``SipMetadataType`` that is defined during the `initialization`_. The new
record contains one file, ``crab.txt``, that contains the words
"head crab" and is created with the this metadata:

.. code:: json

   {
       "$schema": "https://zenodo.org/schemas/deposits/records/record-v1.0.0.json",
       "_deposit": {
           "status": "draft"
       },
       "title": "demo"
   }

The final step is to create a SIP that containing the new record.

.. code:: python

   sip = RecordSIP.create(pid, record, True, user_id=1,
                          agent={'demo': 'archivematica'})
   db.session.commit()

You can now check the admin menu of Invenio to see the SIP object and the
Archive object.

Transfer to Archivematica
-----------------------------------
After we created the SIP we can copy the files to the Archivematica transfer
folder:

.. code:: python

   oais_start_transfer(sip.sip.id, 'test-demo-archivematica')

*Note*: the string you give as a second parameter to the function,
``test-demo-archivematica``, is t he accession ID. This is used to reference
your Archive in the API.

Once the transfer is started, i.e. the files are copied to the transfer folder,
you can run the automation tools:

.. code:: bash

   $ cd /etc/archivematica/automation-tools/
   $ sudo -u archivematica ./transfer-script.sh

The first time you run the automation tools, the processing will check the
transfer folder for new transfers. Once the new transfer is located it will
automatically start the transfer. You can check the progress of the transfer on
the web UI of Archivematica, first in the *Transfer* tab, and then in the
*Ingest* tab, until the AIP is created and stored.

Once the processing is completed you should run the automation-tools again. This
tim the automation-tools will see that the processing is completed and send an
update to Invenio. After this update the Invenio dashboard will show that the
process is finished and the files are correctly archived.

The final step is to fully automate the automation-tools via cron. How often you
wish to call the script can depends on your service. Choose the timescale that
works best for your service.

Invenio-Archivematica API
=========================

The Invenio-Archivematica module exposes the ``oais/archive`` endpoint. This
end point can be used for querying the statis of Archive objects, update the
status of an Archive object and downloading the AIP of archived objects.

Authentication
--------------
The ``oais/archive`` endpoint is protected. For authentication you need the
following items:

1. An API key for your Invenio user.
2. The following permissions for your Invenio user: ``archive-read``,
   ``archive-write``

The API token can be used in the Header or in the url arguments of the request.
Each of these requests will get the status of the Archive object with id
``$ACCESSION_ID`` using API token ``$TOKEN``:

.. code:: bash

   curl -i -X GET -H "Content-Type:application/json" -H "Authorization:Bearer $TOKEN" "http://127.0.0.1/api/oais/archive/$ACCESSION_ID/"
   curl -i -X GET -H "Content-Type:application/json" "http://127.0.0.1/api/oais/archive/$ACCESSION_ID/?access_token=$TOKEN"

GET information about Archive object
------------------------------------
You can access information about a specific Archive object on this end point:

::

   GET /api/oais/archive/$ACCESSION_ID/

It returns a JSON object with the following keys:

-  accession_id
-  archivematica_id
-  sip_id
-  status

If the object has an ``archivematica_id``, this means that there exists an
Archivematica transfer for this object. To get the status of the Archivematica
transfer add the ``realStatus`` flag to the request. This will force Invenio to
report on the real Archivematica status, instead of relying on the status
updates provided by the automation tools. The flag is passed as JSON parameter:

.. code:: bash

   curl -H "Content-Type: application/json" -X GET -d '{"realStatus": true}' 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/?access_token=$TOKEN'


Update information about Archive object
---------------------------------------
To update the status of an Archive object, either manual or via the
automation-tools, you can use this end point:

::

   PATCH /api/oais/archive/$ACCESSION_ID/

With this method, you can change the status and/or the archivematica ID. The
request should contain a JSON dict with the information you want to update:

.. code:: bash

   curl -H "Content-Type: application/json" -X PATCH -d '{"archivematica_id": "fa1391d1-1a78-493a-8e26-f10293706e37"}' 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/?access_token=$TOKEN'

Download an AIP
---------------
After a succesfull transfer you might want to insepct the AIP. To download the
AIP of a transfer with ``$ACCESSION_ID`` you can use the following endpoint:

::

   GET /api/oais/archive/$ACCESSION_ID/download/

The AIP will be streamed to you from the storage. Note that the Archive
*must* have status ``REGISTERED``, so the process on the
Archivematica machines is complete, and the AIP is correctly stored. To download
the AIP create in the `previous section <Archiving a record_>`_ simply run:

.. code:: bash

   wget 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/download/?access_token=$TOKEN'
