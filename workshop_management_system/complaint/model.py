"""Complaint Models.

Description:
- This module contains model for Complaint table.

"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.customer.model import CustomerTable
from workshop_management_system.database.connection import BaseTable


class ComplaintTable(BaseTable):
    """Complaint Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    customer: Mapped["CustomerTable"] = relationship(
        back_populates="complaints"
    )
