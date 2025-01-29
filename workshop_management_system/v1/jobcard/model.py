"""JobCard Model.

Description:
- This module contains model for jobcard table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.customer.model import Customer
    from workshop_management_system.v1.employee.model import Employee
    from workshop_management_system.v1.service.model import Service
    from workshop_management_system.v1.service_item.model import ServiceItem
    from workshop_management_system.v1.vehicle.model import Vehicle


class JobCard(Base, table=True):
    """Job Card Table."""

    jobcard_id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    vehicle_id: int = Field(foreign_key="vehicle.id")
    service_date: datetime
    status: str = Field(max_length=50)
    total_amount: float = Field(max_digits=10, decimal_places=2)
    supervisor_id: int = Field(foreign_key="employee.id")
    mechanic_id: int = Field(foreign_key="employee.id")

    customer: "Customer" = Relationship(back_populates="job_cards")
    vehicle: "Vehicle" = Relationship(back_populates="job_cards")
    supervisor: "Employee" = Relationship(
        back_populates="supervised_jobs",
        sa_relationship_kwargs={"foreign_keys": "[JobCard.supervisor_id]"},
    )
    mechanic: "Employee" = Relationship(
        back_populates="mechanic_jobs",
        sa_relationship_kwargs={"foreign_keys": "[JobCard.mechanic_id]"},
    )
    services: list["Service"] = Relationship(back_populates="job_card")
    service_items: list["ServiceItem"] = Relationship(
        back_populates="job_card"
    )
