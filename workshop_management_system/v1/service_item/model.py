"""ServieItem Models.

Description:
- This module contains model for servieitem table.
"""

from typing import Any

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable


class ServiceItemTable(BaseTable):
    """Service Item Table."""

    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    item_name: Mapped[str] = mapped_column(String(255))
    item_description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    discount: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    total_amount: MappedColumn[Any] = mapped_column(Numeric(10, 2))
