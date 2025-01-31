"""Inventory Models.

Description:
- This module contains model for inventory table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.service_item.model import ServiceItem
    from workshop_management_system.v1.stock_transaction.model import (
        StockTransaction,
    )
    from workshop_management_system.v1.supplier.model import Supplier


class Inventory(Base, table=True):
    """Inventory Table."""

    # inventory_id: int | None = Field(default=None, primary_key=True)
    item_name: str = Field(max_length=255)
    quantity: int
    unit_price: float = Field(max_digits=10, decimal_places=2)
    supplier_id: int = Field(foreign_key="supplier.id")
    minimum_stock_level: int

    supplier: "Supplier" = Relationship(back_populates="inventory_items")
    transactions: list["StockTransaction"] = Relationship(
        back_populates="inventory"
    )
    service_items: list["ServiceItem"] = Relationship(
        back_populates="inventory"
    )
