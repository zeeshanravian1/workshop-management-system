"""Supplier Models.

Description:
- This module contains model for Supplier table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.inventory.model import Inventory


class Supplier(Base, table=True):
    """Supplier Table."""

    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    contact_number: str = Field(max_length=20)
    address: str = Field()
    inventory_items: list["Inventory"] = Relationship(
        back_populates="supplier"
    )
