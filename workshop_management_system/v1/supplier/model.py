"""Supplier Model.

Description:
- This module contains model for supplier table.
"""

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base


class Supplier(Base, table=True):
    """Supplier Table."""

    name: str = Field(max_length=255)
    contact_number: str = Field(max_length=20)
    address: str = Field()
    inventory_items: list["Inventory"] = Relationship(
        back_populates="supplier"
    )
