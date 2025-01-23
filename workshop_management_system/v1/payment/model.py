"""Payment Models.

Description:
- This module contains model for payment table.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.customer.model import CustomerTable


class PaymentTable(BaseTable):
    """Payment Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    amount: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    payment_date: Mapped[datetime] = mapped_column(DateTime)
    payment_method: Mapped[str] = mapped_column(String(50))
    reference_number: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    customer: Mapped["CustomerTable"] = relationship(back_populates="payments")
