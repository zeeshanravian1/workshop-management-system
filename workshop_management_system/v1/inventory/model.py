"""Inventory Models.

Description:
- This module contains model for inventory table.
"""

from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.supplier.model import Supplier


class Inventory(Base, table=True):
    """Inventory Table."""

    item_name: str = Field(max_length=255)
    quantity: int
    unit_price: float = Field(max_digits=10, decimal_places=2)
    supplier_id: UUID = Field(foreign_key="supplier.id")
    minimum_stock_level: int

    supplier: Supplier = Relationship(back_populates="inventory_items")
    transactions: list["StockTransaction"] = Relationship(
        back_populates="inventory"
    )
