"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.customer.model import CustomerTable


class VehicleTable(BaseTable, table=True):
    """Vehicle Table."""

    make: str = Field(max_length=100)
    model: str = Field(max_length=100)
    year: int
    chassis_number: str = Field(max_length=50)
    engine_number: str = Field(max_length=50)
    customer_id: UUID = Field(foreign_key="customertable.id")

    customer: CustomerTable = Relationship(back_populates="vehicles")
