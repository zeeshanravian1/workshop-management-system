"""Estimate Model Module."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from ..customer.model import Customer
    from ..jobcard.model import JobCard
    from ..vehicle.model import Vehicle


class Estimate(Base, table=True):
    """Estimate Table."""

    estimate_date: datetime = Field()
    total_estimate_amount: float = Field(default=0.0)
    status: str = Field(max_length=50)
    valid_until: datetime
    description: str | None = Field(max_length=255, default=None)
    vehicle_id: int = Field(foreign_key="vehicle.id")
    job_card_id: int | None = Field(foreign_key="jobcard.id", default=None)
    customer_id: int | None = Field(foreign_key="customer.id")

    vehicle: "Vehicle" = Relationship(back_populates="estimates")
    job_card: Optional["JobCard"] = Relationship(back_populates="estimates")
    customer: Optional["Customer"] = Relationship(back_populates="estimates")
