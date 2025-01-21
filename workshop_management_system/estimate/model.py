"""Estimate Models.

Description:
- This module contains model for estimate table.
"""

from datetime import datetime

from sqlalchemy import DateTime, Decimal, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from workshop_management_system.database.connection import BaseTable


class EstimateTable(BaseTable):
    """Estimate Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    estimate_date: Mapped[datetime] = mapped_column(DateTime)
    total_estimate_amount: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    status: Mapped[str] = mapped_column(String(50))
