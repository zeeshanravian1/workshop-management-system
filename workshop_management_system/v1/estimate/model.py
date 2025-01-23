"""Estimate Models.

Description:
- This module contains model for estimate table.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable


class EstimateTable(BaseTable):
    """Estimate Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    estimate_date: Mapped[datetime] = mapped_column(DateTime)
    total_estimate_amount: MappedColumn[Any] = mapped_column(
        Numeric(precision=10, decimal_return_scale=2)
    )
    status: Mapped[str] = mapped_column(String(50))
