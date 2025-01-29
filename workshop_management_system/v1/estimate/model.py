"""Estimate Models.

Description:
- This module contains model for estimate table.
"""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.vehicle.model import Vehicle


class Estimate(Base, table=True):
    """Estimate Table."""

    estimate_date: datetime = Field()
    total_estimate_amount: float = Field(default=0.0)
    status: str = Field(max_length=50)
    description: str | None = Field(max_length=255, default=None)
    customer_id: UUID = Field(foreign_key="customer.id")
    vehicle_id: UUID = Field(foreign_key="vehicle.id")

    customer: Customer = Relationship(back_populates="estimates")
    vehicle: Vehicle = Relationship(back_populates="estimates")
