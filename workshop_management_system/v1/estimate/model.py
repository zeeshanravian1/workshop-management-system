"""Estimate Models.

Description:
- This module contains model for estimate table.
"""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.customer.model import CustomerTable
from workshop_management_system.v1.vehicle.model import VehicleTable


class EstimateTable(BaseTable, table=True):
    """Estimate Table."""

    estimate_date: datetime = Field()
    total_estimate_amount: float = Field(default=0.0)
    status: str = Field(max_length=50)
    description: str | None = Field(max_length=255, default=None)
    customer_id: UUID = Field(foreign_key="customertable.id")
    vehicle_id: UUID = Field(foreign_key="vehicletable.id")

    customer: CustomerTable = Relationship(back_populates="estimates")
    vehicle: VehicleTable = Relationship(back_populates="estimates")
