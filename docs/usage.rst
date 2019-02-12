..
    This file is part of Invenio.
    Copyright (C) 2017-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Prerequisites
-------------
The following will assume that you have Invenio, Invenio-Archivematica, Archivematica 
and the automation-tools installed.


Concepts
--------

This is how the Invenio to Archivematica workflow works:

1. on Invenio, you create a SIP representing what you want to archive

   -  it contains files
   -  it contains metadata

      -  only the metadata with the type listed in
         ``SIPSTORE_ARCHIVER_METADATA_TYPES`` will be archived

   -  you can see your SIP in the Invenio admin menu: ``/admin/sip/``

2. an Archive object is automatically created, with the status ``NEW``
   so it hasn’t been sent to Archivematica yet

   -  you can see the Archive object in the Invenio admin menu:
      ``/admin/archive/``

3. you start the transfer to Archivematica

   -  the Archive is updated with the status ``WAITING``
   -  the files and metadata are sent to the transfer folder of
      Archivematica waiting for processing

4. Archivematica starts processing the files and notifies Invenio about the
   process
5. the files are stored in the storage inside an AIP

You understand that the SIP at the origin of the process needs to be
created. For the moment, this is not automatically generated, but you
can generate one thanks to the ``create_archive.py`` script, see below.

On the dashboard, the Automation-Tools should be run every X minutes
thanks to a cron script. You can eventually trigger it manually.

If the Automation-Tools is not able to notify Invenio about the process
for some reasons, you will have to call the Invenio-Archivematica API
yourself.

Let’s archive a record
----------------------

Here, we will follow the code described in
https://github.com/inveniosoftware/invenio-archivematica/blob/master/examples/create_archive.py
step by step.

Initialization
^^^^^^^^^^^^^^

On the web container, run the Invenio shell. Note that you need to
import all the stuff at the beginning of the script:

-  ``docker exec -it invenio_web_1 bash``, or for OpenShift,
   ``oc rsh dc/web``
-  ``invenio shell``

Copy / paste the imports:

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

If you didn’t setup manually the locations, then the first time you need
to run this:

.. code:: python

    try:
        makedirs('/archive/')
    except:
        pass
    locrecords = Location(
        name='records',
        uri='',     # insert here the directory where you wanr your records to go
        default=True
    )
    locarchive = Location(
        name='archive',  # this should go in SIPSTORE_ARCHIVER_LOCATION_NAME
        uri='' # insert here the directory shared with archivematica
    )
    db.session.add(locrecords)
    db.session.add(locarchive)
    db.session.commit()

The first location is the one where the records are saved. These are not yet shipped
to Archivematica. Once they appear in the second location (loarchive) they are 
in Archivematica's location.

Note that the name of the archive location **needs** to be the same as the name
put in the variable ``SIPSTORE_ARCHIVER_LOCATION_NAME``.

Now we create a metadata type. Here, the name of the metadata type
**must** appear in the config variable
``SIPSTORE_ARCHIVER_METADATA_TYPES``. The schema used **must** be the
same as the one used when we will create the record.

.. code:: python

   mtype = SIPMetadataType(title='Invenio JSON test',
                           name='invenio-json-test',
                           format='json',
                           schema='https://zenodo.org/schemas/deposits/records/record-v1.0.0.json')
   db.session.add(mtype)
   db.session.commit()

Create a record with files
^^^^^^^^^^^^^^^^^^^^^^^^^^

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

The created record must have the key ``$schema`` with the same value as
the metadata type’s schema.

Here, we have created a simple record with the following metadata:

.. code:: json

   {
       "$schema": "https://zenodo.org/schemas/deposits/records/record-v1.0.0.json",
       "_deposit": {
           "status": "draft"
       },
       "title": "demo"
   }

It also contains one file ``crab.txt`` that contains the words
``head crab``.

Create the SIP
^^^^^^^^^^^^^^

Here we start the Invenio to Archivematica workflow:

.. code:: python

   sip = RecordSIP.create(pid, record, True, user_id=1, agent={'demo': 'archivematica'})
   db.session.commit()

You can now check the admin menu of Invenio to see the SIP object and the Archive
object.

Start the transfer on Archivematica
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here, we send the files to the Archivematica transfer folder:

.. code:: python

   oais_start_transfer(sip.sip.id, 'test-demo-archivematica')

**IMPORTANT**: note that the string you give as a second parameter to
the function, here ``test-demo-archivematica``, will be the accession
ID, used to retrieve your Archive in the API.

Run the Automation-Tools on Archivematica
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You now need to log into the dashboard to run the Automation-Tools and
start the processing of the files by Archivematica. Log into the
Dashboard machine and do:

.. code:: bash

   $ su archivematica
   $ cd /home/archivematica/automation-tools/
   $ ./run-automation-tools.sh
   # ...

The first time you run it, the processing will start, you can follow it
on the web UI of Archivematica, first in the *Transfer* tab, and then in
the *Ingest* tab, until the AIP is created and stored.

Then, if you run again the script ``run-automation-tools.sh``, it will
see the current processing step and it **should** notify Invenio about
it. If you run it once it is finished, it will say to Invenio that the
process is finished and the files are correctly archived.

If this doesn’t work, you can update Invenio yourself with the following
API.

Eventually you can run the automation-tools via cron to fully automate 
the process. How often you wish call the script can depend on your service.
Choose the timescale that works for your service.

Invenio-Archivematica API
-------------------------

The Invenio-Archivematica module creates the following API end points.
You need to note that all end points are protected:

-  you need an API key linked to your user to access it
-  the user needs to have the following permissions:

   -  archive-read
   -  archive-write

To access an API end point, you need to give your API key, either in the
header or in the URL parameters. These 2 CURL requests are OK:

-  ``curl -i -X GET -H "Content-Type:application/json" -H "Authorization:Bearer $TOKEN" "http://127.0.0.1/api/oais/archive/$ACCESSION_ID/"``
-  ``curl -i -X GET -H "Content-Type:application/json" "http://127.0.0.1/api/oais/archive/$ACCESSION_ID/?access_token=$TOKEN"``

As you can see, you access to an Archive object via its accession ID.
This is the string you gave to the function ``oais_start_transfer``
before, by default it is ``test-demo-archivematica``.

GET information about Archive object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can access information about an Archive object on this end point:

::

   GET /api/oais/archive/$ACCESSION_ID/

It returns a JSON object with the following keys:

-  accession_id
-  archivematica_id
-  sip_id
-  status

If it has an ``archivematica_id``, then you can add a JSON parameter to
this request so Invenio-Archivematica will query Archivematica to know
the read status. For instance, if the status returned is ``PROCESSING``,
it may now be finished on Archivematica, but Invenio doesn’t know yet as
the Automation-Tools hasn’t been run yet.

Thus, you can run this query:

.. code:: bash

   curl -H "Content-Type: application/json" -X GET -d '{"realStatus": true}' 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/?access_token=$TOKEN'

Note the ``realStatus`` parameter.

Update information about Archive object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use this end point:

::

   PATCH /api/oais/archive/$ACCESSION_ID/

With this method, you can change the status and/or the archivematica ID.
Just send a JSON dict with the informations you want to update:

.. code:: bash

   curl -H "Content-Type: application/json" -X PATCH -d '{"archivematica_id": "fa1391d1-1a78-493a-8e26-f10293706e37"}' 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/?access_token=$TOKEN'

Download an AIP
~~~~~~~~~~~~~~~

You can download an AIP from this end point:

::

   GET /api/oais/archive/$ACCESSION_ID/download/

The AIP will be streamed to you from the storage. Note that the Archive
**must** have a status ``REGISTERED``, so the process on the
Archivematica machines is complete, and the AIP is correctly stored.

Example:

.. code:: bash

   wget 'http://127.0.0.1/api/oais/archive/test-demo-archivematica/download/?access_token=$TOKEN'
