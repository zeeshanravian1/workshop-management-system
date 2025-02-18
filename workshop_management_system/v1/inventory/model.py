"""Inventory Models.

Description:
- This module contains model for inventory table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.inventory.association import (
    InventoryEstimate,
)

if TYPE_CHECKING:
    from workshop_management_system.v1.estimate.model import Estimate
    from workshop_management_system.v1.supplier.model import Supplier


class Inventory(Base, table=True):
    """Inventory Table."""

    item_name: str = Field(max_length=255)
    quantity: int
    unit_price: float = Field(max_digits=10, decimal_places=2)
    minimum_stock_level: int
    category: str = Field(max_length=50)
    reorder_level: int
    supplier_id: int = Field(foreign_key="supplier.id")
    supplier: "Supplier" = Relationship(back_populates="inventory_items")
    estimates: list["Estimate"] = Relationship(
        back_populates="inventories", link_model=InventoryEstimate
    )
