"""ServieItem Models.

Description:
- This module contains model for servieitem table.
"""

from sqlalchemy import Decimal, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from workshop_management_system.database.connection import BaseTable


class ServiceItemTable(BaseTable):
    """Service Item Table."""

    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    item_name: Mapped[str] = mapped_column(String(255))
    item_description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    discount: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    total_amount: Mapped[Decimal] = mapped_column(Decimal(10, 2))
