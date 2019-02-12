..
    This file is part of Invenio.
    Copyright (C) 2017-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


************
Installation
************

Invenio-Archivematica requires you to have Invenio and Archivematica installed.

Head over to `invenio’s docs <https://invenio.readthedocs.io/en/latest/>`_
if you have not installed it yet and follow the guide.

If you have not yet installed Archivematica head over to `Archivematica <https://www.archivematica.org/en/docs/archivematica-1.8/admin-manual/installation-setup/installation/installation/#installation>`_ to install it.

Install Invenio-Archivematica
=============================
Before installing the Invenio-Archivematica module stop any running Invenio instance.

Download or clone the github repository `inveniosoftware/invenio-archivematica <https://github.com/inveniosoftware/invenio-archivematica>`_ and then go to its root directory and *pip install*:

::

   $ cd invenio-archivematica/
   $ pip install .[all]

(**Note**: the ``--editable`` option is used for development. It means
that if you change the files in the module, you won’t have to reinstall
it to see the changes. In a production environment, this option
shouldn’t be used.)

Set up a transfer folder
========================
To link Invenio and Archivematica a transfer folder needs to be set up. 

This is the folder to which the SIPs of Invenio will be copied and from which transfers into Archivematica can be started.
The Invenio user needs read and write access and archivematica needs read access as well.

Install automation-tools
========================
To automate the connection between Invenio and Archivematica the installation of the automation-tools will be needed.
For this you can follow the installation tutorial `here <https://github.com/CERN-E-Ternity/automation-tools>`_.

***********
Development
***********

For development it can be useful to install every component locally.

Archivematica
=============
For development there is the possibility to `install Archivematica locally using Docker Compose on Linux <https://github.com/artefactual-labs/am/tree/master/compose#docker-and-linux>`_.
When you are running Invenio locally as well and have used the standard configuration there should be no conflict between the Docker containers' ports.

The default username and password for Archivematica are ``test`` and ``test``.

Invenio-Archivematica
=====================
Follow the steps described above. For development the ``--editable`` option can be used for pip install. 

This means that if you change the files
in the module, you won’t have to reinstall the module before seeing changes. This should not be used in a production environment.

::

   $ cd invenio-archivematica/
   $ pip install .[all]

Transfer-folder
===============
When installing Archivematica via Docker the folder needs to be mounted so that the Dashboard can access it.

For testing purposes it is also possible to use the ``.am`` directory in the ``Home`` directory, which is already used by the Docker containers.
By creating a transfer folder in it and changing the rights so that the Invenio user can read and write,
the transfer folder will be usable for development.

Automation-tools
================
The automation-tools are a set of scripts which are used to automate the process of archiving the SIPs into Archivematica.
An installation guide can be found `here <https://github.com/CERN-E-Ternity/automation-tools>`_.

**Note**: The location of the repo locally can be changed. Same goes for the location of the virtual environment (for this, change the directory when running, as well). The directories for the log/database/PID files can be changed as well.
For this change the ``/automation-tools/etc/transfers.conf`` to lead to the chosen directory. 
For it to be used you need to use the ``-c`` option: 

    ``-c FILE, --config-file FILE`` config file containing file paths for log/database/PID files. Default: log/database/PID files stored in the same directory as the script (not recommended for production).

Further automation
==================
In the standard configuration of Archivematica the transfer and ingest process require user interaction. 
For automation of this, you can change the processing configuration in the Archivematica dashboard to suit your needs.

The following configuration automates every step possible. Please note that this will automatically approve every transfer and ingest without giving you the possibility to check before storing the AIP.

    **Send transfer to quarantine:** No

    **Remove from quarantine after (days):** 0

    **Generate transfer structure report:** No

    **Select file format identification command (Transfer):** Identify using Fido

    **Extract packages:** Yes

    **Delete packages after extraction:** Yes

    **Examine contents:** Skip examine contents

    **Create SIP(s):** Create single SIP and continue processing

    **Select file format identification command (Ingest):** Use existing data

    **Normalize:** Normalize for preservation

    **Approve normalization:** Yes

    **Reminder:** add metadata if desired: Continue

    **Transcribe files (OCR):** No

    **Select file format identification command (Submission documentation & metadata):** Skip file identification

    **Select compression algorithm:** 7z using bzip2

    **Select compression level:** 5 - normal compression mode 

    **Store AIP:** Yes

    **Store AIP location:** <change to your desired location>

    **Store DIP location:** <change to your desired location>

