"""Payment Models.

Description:
- This module contains model for payment table.
"""

from datetime import datetime

from sqlalchemy import DateTime, Decimal, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.customer.model import CustomerTable
from workshop_management_system.database.connection import BaseTable


class PaymentTable(BaseTable):
    """Payment Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    amount: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    payment_date: Mapped[datetime] = mapped_column(DateTime)
    payment_method: Mapped[str] = mapped_column(String(50))
    reference_number: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    customer: Mapped["CustomerTable"] = relationship(back_populates="payments")
