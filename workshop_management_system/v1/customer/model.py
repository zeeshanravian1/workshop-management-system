"""Customer Model.

Description:
- This module contains model for Customer table.

"""

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base


class Customer(Base, table=True):
    """Customer Table."""

    name: str = Field(max_length=2_55)
    mobile_number: str = Field(max_length=20)
    vehicle_registration_number: str = Field(max_length=50)
    email: str = Field(max_length=255)
    address: str

    vehicles: list["Vehicle"] = Relationship(back_populates="customer")
