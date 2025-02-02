"""DigitalSignature Models.

Description:
- This module contains model for digitalsignature table.
"""

from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.customer.model import Customer


class DigitalSignature(Base, table=True):
    """Digital Signature Table."""

    customer_id: UUID = Field(foreign_key="customer.id")
    minio_path: str = Field(max_length=500)  # Store MinIO object path/URL
    bucket_name: str = Field(max_length=255)  # Store MinIO bucket name
    object_name: str = Field(max_length=255)  # Store MinIO object name

    customer: Customer = Relationship(back_populates="digital_signatures")
