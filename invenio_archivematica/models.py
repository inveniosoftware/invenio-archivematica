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

"""Archive models."""

from enum import Enum

from flask_babelex import gettext
from invenio_db import db
from invenio_records.models import RecordMetadata
from speaklater import make_lazy_gettext
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils.types import ChoiceType, UUIDType

_ = make_lazy_gettext(lambda: gettext)


ARCHIVE_STATUS_TITLES = {
    'NEW': _('New'),
    'WAITING': _('Waiting'),
    'PROCESSING_TRANSFER': _('Processing Transfer'),
    'PROCESSING_AIP': _('Processing AIP'),
    'REGISTERED': _('Registered'),
    'FAILED': _('Failed'),
    'IGNORED': _('Ignored'),
    'DELETED': _('Deleted'),
}


class ArchiveStatus(Enum):
    """Constants for possible status of any given Archive object."""

    NEW = 'NEW'
    """The record has been created or updated, but not yet archived."""

    WAITING = 'WAITING'
    """The record has been transfered, and is waiting for processing."""

    PROCESSING_TRANSFER = 'PROCESSING_TRANSFER'
    """The record is currently being processed as a transfer (first step)."""

    PROCESSING_AIP = 'PROCESSING_AIP'
    """The record is currently being processed as an AIP (final step)."""

    REGISTERED = 'REGISTERED'
    """The record has been archived."""

    FAILED = 'FAILED'
    """The record has not been archived because of an error."""

    IGNORED = 'IGNORED'
    """The record won't be archived."""

    DELETED = 'DELETED'
    """The archive has been deleted."""

    def __eq__(self, other):
        """Equality test."""
        return self.value == other

    def __str__(self):
        """Return its value."""
        return self.value

    @property
    def title(self):
        """Return human readable title."""
        return ARCHIVE_STATUS_TITLES[self.name]


class ArchivematicaStatus(Enum):
    """Constants for status of AIPs provided by Archivematica."""


class Archive(db.Model):
    """Registers the status of a record: archived or not.

    The status is a member of
    :py:class:`invenio_archivematica.models.ArchiveStatus`.

    A record can have only one archive, and an archive applies to only
    one record.
    """

    __tablename__ = 'archivematica_archive'
    __table_args__ = (
        db.Index('idx_ark_record', 'record_id'),
        db.Index('idx_ark_status', 'status')
    )

    id = db.Column(db.BigInteger, primary_key=True)
    """ID of the Archive object."""

    record_id = db.Column(
        UUIDType,
        db.ForeignKey(RecordMetadata.id, name='fk_archivematica_record_id'),
        nullable=False
    )
    """Record related with the Archive."""

    status = db.Column(ChoiceType(ArchiveStatus, impl=db.String(20)),
                       nullable=False)

    aip_accessioned_id = db.Column(db.String(255), nullable=True, unique=True)
    """Accessioned ID of the AIP in Archivematica."""

    aip_id = db.Column(UUIDType, nullable=True)
    """ID of the AIP in Archivematica."""

    # Relations
    record = db.relationship(RecordMetadata)
    """Relationship with Records."""

    #
    # Class methods
    #
    @classmethod
    def create(cls, record, aip_accessioned_id=None, aip_id=None):
        """Create a new Archive object and add it to the session.

        The new Archive object will have a NEW status
        :param record: the record attached to the archive
        :type record: :py:class:`invenio_records.models.RecordMetadata`
        :param str aip_accessioned_id: the accessioned ID of the AIP
        :param str aip_id: The UUID of the AIP
        """
        ark = cls(record=record,
                  status=ArchiveStatus.NEW,
                  aip_accessioned_id=aip_accessioned_id,
                  aip_id=aip_id)
        db.session.add(ark)
        return ark

    @classmethod
    def get_from_record(cls, uuid):
        """Return the Archive object associated to the given record.

        It tries to get the Archive object associated to the record. If it
        exists, it returns it, otherwise it returns None.
        :param str uuid: the uuid of the record
        :rtype: :py:class:`invenio_archivematica.models.Archive` or None
        """
        try:
            return cls.query.filter_by(record_id=uuid).one()
        except NoResultFound:
            return None

    @classmethod
    def get_from_accession_id(cls, accession_id):
        """Return the Archive object associated to the given record.

        If the accession_id is not in the table, it returns None.
        :param str accession_id: the accession_id of the Archive object.
        :rtype: :py:class:`invenio_archivematica.models.Archive` or None
        """
        try:
            return cls.query.filter_by(aip_accessioned_id=accession_id).one()
        except NoResultFound:
            return None
