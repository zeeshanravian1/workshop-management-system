"""DigitalSignature Models.

Description:
- This module contains model for digitalsignature table.

"""

from sqlalchemy import BLOB, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from workshop_management_system.database.connection import BaseTable


class DigitalSignatureTable(BaseTable):
    """Digital Signature Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    signature_image: Mapped[bytes] = mapped_column(BLOB)
