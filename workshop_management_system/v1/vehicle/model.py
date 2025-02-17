"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from ..customer.model import Customer
    from ..estimate.model import Estimate
    from ..jobcard.model import JobCard

from workshop_management_system.database.connection import Base


class Vehicle(Base, table=True):
    """Vehicle Table."""

    make: str = Field(max_length=100)
    model: str = Field(max_length=100)
    year: int
    vehicle_number: str = Field(max_length=50)
    chassis_number: str = Field(max_length=50)
    engine_number: str = Field(max_length=50)
    customer_id: int = Field(foreign_key="customer.id")

    customer: Optional["Customer"] = Relationship(back_populates="vehicles")
    estimates: list["Estimate"] = Relationship(back_populates="vehicle")
    job_cards: list["JobCard"] = Relationship(back_populates="vehicle")
