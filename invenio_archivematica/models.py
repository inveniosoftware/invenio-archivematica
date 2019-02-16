# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Archive models."""

from enum import Enum

from flask_babelex import gettext
from invenio_db import db
from invenio_sipstore.models import SIP
from speaklater import make_lazy_gettext
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import ChoiceType, UUIDType

_ = make_lazy_gettext(lambda: gettext)


ARCHIVE_STATUS_TITLES = {
    'NEW': _('New'),
    'WAITING': _('Waiting'),
    'PROCESSING_TRANSFER': _('Processing Transfer'),
    'FAILED_TRANSFER': _('Failed Transfer'),
    'PROCESSING_AIP': _('Processing AIP'),
    'REGISTERED': _('Registered'),
    'FAILED': _('Failed'),
    'IGNORED': _('Ignored'),
    'DELETED': _('Deleted'),
}


class ArchiveStatus(Enum):
    """Constants for possible status of any given Archive object."""

    NEW = 'NEW'
    """The sip has been created or updated, but not yet archived."""

    WAITING = 'WAITING'
    """The sip has been transfered, and is waiting for processing."""

    PROCESSING_TRANSFER = 'PROCESSING_TRANSFER'
    """The sip is currently being processed as a transfer (first step)."""

    PROCESSING_AIP = 'PROCESSING_AIP'
    """The sip is currently being processed as an AIP (final step)."""

    REGISTERED = 'REGISTERED'
    """The sip has been archived."""

    FAILED_TRANSFER = 'FAILED_TRANSFER'
    """The transfer of sip failed."""

    FAILED = 'FAILED'
    """The sip has not been archived because of an error."""

    IGNORED = 'IGNORED'
    """The sip won't be archived."""

    DELETED = 'DELETED'
    """The archive has been deleted."""

    def __eq__(self, other):
        """Equality test."""
        return self.value == other

    def __hash__(self):
        """Hash for dictionaries."""
        return hash(self.value)

    def __str__(self):
        """Return its value."""
        return self.value

    @property
    def title(self):
        """Return human readable title."""
        return ARCHIVE_STATUS_TITLES[self.name]


def status_converter(status, aip_processing=False):
    """Convert a status given by Archivematica into an ArchiveStatus.

    :param str status: a status returned by an Archivematica API
    :param bool aip_processing: tells if it is processing the AIP or the
        transfer
    """
    statuses = {
        'AIP_PROCESSING': ArchiveStatus.PROCESSING_AIP,
        'COMPLETE': ArchiveStatus.REGISTERED,
        'DELETED': ArchiveStatus.DELETED,
        'FAILED': ArchiveStatus.FAILED,
        'IGNORED': ArchiveStatus.IGNORED,
        'NEW': ArchiveStatus.NEW,
        'PROCESSING_AIP': ArchiveStatus.PROCESSING_AIP,
        'PROCESSING_TRANSFER': ArchiveStatus.PROCESSING_TRANSFER,
        'REGISTERED': ArchiveStatus.REGISTERED,
        'REJECTED': ArchiveStatus.FAILED,
        'SIP_PROCESSING': ArchiveStatus.PROCESSING_TRANSFER,
        'USER_INPUT': ArchiveStatus.FAILED,
        'WAITING': ArchiveStatus.WAITING
    }
    if status == 'PROCESSING' and aip_processing:
        status = 'AIP_PROCESSING'
    elif status == 'PROCESSING':
        status = 'SIP_PROCESSING'
    return statuses[status]


class Archive(db.Model, Timestamp):
    """Registers the status of a sip: archived or not.

    The status is a member of
    :py:class:`invenio_archivematica.models.ArchiveStatus`.

    A sip can have only one archive, and an archive applies to only
    one sip.
    """

    __tablename__ = 'archivematica_archive'
    __table_args__ = (
        db.Index('idx_ark_sip', 'sip_id'),
        db.Index('idx_ark_status', 'status'),
        db.Index('idx_ark_accession_id', 'accession_id')
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, 'sqlite'),
                   primary_key=True)
    """ID of the Archive object."""

    sip_id = db.Column(
        UUIDType,
        db.ForeignKey(SIP.id, name='fk_archivematica_sip_id'),
        nullable=False
    )
    """SIP related with the Archive."""

    status = db.Column(ChoiceType(ArchiveStatus, impl=db.String(20)),
                       nullable=False)
    """Status of the archive."""

    accession_id = db.Column(db.String(255), nullable=True, unique=True)
    """Accessioned ID of the AIP in Archivematica."""

    archivematica_id = db.Column(UUIDType, nullable=True)
    """ID of the AIP in Archivematica."""

    # Relations
    sip = db.relationship(SIP)
    """Relationship with SIP."""

    #
    # Class methods
    #
    @classmethod
    def create(cls, sip, accession_id=None, archivematica_id=None):
        """Create a new Archive object and add it to the session.

        The new Archive object will have a NEW status

        :param sip: the sip attached to the archive
        :type sip: :py:class:`invenio_sipstore.models.SIP`
        :param str accession_id: the accession ID of the AIP
        :param str archivematica_id: The UUID of the AIP
        """
        ark = cls(sip=sip,
                  status=ArchiveStatus.NEW,
                  accession_id=accession_id,
                  archivematica_id=archivematica_id)
        db.session.add(ark)
        return ark

    @classmethod
    def get_from_sip(cls, uuid):
        """Return the Archive object associated to the given sip.

        It tries to get the Archive object associated to the sip. If it
        exists, it returns it, otherwise it returns None.

        :param str uuid: the uuid of the sip
        :rtype: :py:class:`invenio_archivematica.models.Archive` or None
        """
        return cls.query.filter_by(sip_id=uuid).one_or_none()

    @classmethod
    def get_from_accession_id(cls, accession_id):
        """Return the Archive object associated to the given accession_id.

        If the accession_id is not in the table, it returns None.

        :param str accession_id: the accession_id of the Archive object.
        :rtype: :py:class:`invenio_archivematica.models.Archive` or None
        """
        return cls.query.filter_by(accession_id=accession_id).one_or_none()
