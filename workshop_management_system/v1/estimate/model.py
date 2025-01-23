"""Estimate Models.

Description:
- This module contains model for estimate table.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable


class EstimateTable(BaseTable):
    """Estimate Table."""

    id = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    estimate_date: Mapped[datetime] = mapped_column(DateTime)
    total_estimate_amount: MappedColumn[Any] = mapped_column(
        Numeric(precision=10, decimal_return_scale=2)
    )
    status: Mapped[str] = mapped_column(String(50))
    nhil: MappedColumn[Any] = mapped_column(
        Numeric(precision=5, decimal_return_scale=2)
    )
    getfund: MappedColumn[Any] = mapped_column(
        Numeric(precision=5, decimal_return_scale=2)
    )
    covid_levy: MappedColumn[Any] = mapped_column(
        Numeric(precision=5, decimal_return_scale=2)
    )
    total_levy: MappedColumn[Any] = mapped_column(
        Numeric(precision=10, decimal_return_scale=2)
    )
    vat: MappedColumn[Any] = mapped_column(
        Numeric(precision=5, decimal_return_scale=2)
    )
    total_inclusive_tax: MappedColumn[Any] = mapped_column(
        Numeric(precision=10, decimal_return_scale=2)
    )
