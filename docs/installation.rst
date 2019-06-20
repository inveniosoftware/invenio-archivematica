..
    This file is part of Invenio.
    Copyright (C) 2017-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============

Invenio-Archivematica requires you to have Invenio and Archivematica installed.
Head over to `invenio’s docs <https://invenio.readthedocs.io/en/latest/>`_
if you have not installed it yet and follow the guide.
If you have not yet installed Archivematica head over to `Archivematica
<https://www.archivematica.org/en/docs/archivematica-1.9/admin-manual/installation-setup/installation/installation/#installation>`_
to install it.

If you want to have a local development installation please checout the
instructions for setting up the `Development Setup`_.

Install Invenio-Archivematica
=============================
Before installing the Invenio-Archivematica module stop any running Invenio
instance.

Download or clone the github repository `inveniosoftware/invenio-archivematica
<https://github.com/inveniosoftware/invenio-archivematica>`_ and install using:

::

  cd invenio-archivematica/
  pip install .[all]

Set up a transfer folder
========================
To link Invenio and Archivematica a transfer folder needs to be set up. The
transer folder is a shared resource between Invenio and Archivematica. Invenio
will copy files into the transfer folder. Archivematica will watch the folder
and start ingesting new folders and files. The Invenio user needs read and write
access and archivematica needs read access as well.

Install automation-tools
========================
To automate the connection between Invenio and Archivematica the installationof
the automation-tools will be needed. For this you can follow this `installation
tutorial <https://github.com/inveniosoftware/automation-tools#installation>`_.
After finishing the installation you have to configure for
`further automation`_.

*****************
Development setup
*****************

A convenient way for setting up a development environment is using
docker- compose we advise you to follow this `invenio tutorial
<https://github.com/inveniosoftware/training/tree/master/01-getting-started>`_
and this `archivematica tutorial
<https://github.com/artefactual-labs/am/tree/master/compose>`_.

Before installing the *Invenio-Archivematica* module stop any running Invenio
instance. Download or clone the github repository
`inveniosoftware/invenio-archivematica
<https://github.com/inveniosoftware/invenio-archivematica>`_
and install using:

::

  cd invenio-archivematica/
  pip install --editable .[all]


Set up a transfer folder
========================
To link Invenio and Archivematica a transfer folder needs to be set up. The
transfer folder is a shared resource between Invenio and Archivematica. Invenio
will copy files into the transfer folder. Archivematica will watch the folder
and start ingesting new folders and files.

The default location of the transfer-folder in a local Archivematica setup is
``$HOME/.am/ss-location-data/``. If you run docker using ``sudo`` you might have
to change the access rights of the ``.am`` folder so that Invenio can copy files
into the tranfer folder.

The last step is to `install automation-tools`_ and to configure
`further automation`_.

******************
Further automation
******************
In the standard configuration of Archivematica the transfer and ingest process
require user interaction. For automation of this, you can change the processing
configuration in the Archivematica dashboard to suit your needs.

The following configuration automates every step possible. Please note that this
will automatically approve every transfer and ingest without giving you
the possibility to check before storing the AIP.

    **Send transfer to quarantine:** No

    **Remove from quarantine after (days):** 0

    **Generate transfer structure report:** No

    **Select file format identification command (Transfer):**
    Identify using Fido

    **Extract packages:** Yes

    **Delete packages after extraction:** Yes

    **Examine contents:** Skip examine contents

    **Create SIP(s):** Create single SIP and continue processing

    **Select file format identification command (Ingest):** Use existing data

    **Normalize:** Normalize for preservation

    **Approve normalization:** Yes

    **Reminder:** add metadata if desired: Continue

    **Transcribe files (OCR):** No

    **Select file format identification command (Submission documentation**
    **& metadata):** Skip file identification

    **Select compression algorithm:** 7z using bzip2

    **Select compression level:** 5 - normal compression mode

    **Store AIP:** Yes

    **Store AIP location:** <change to your desired location>

    **Store DIP location:** <change to your desired location>
