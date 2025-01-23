"""Inventory Models.

Description:
- This module contains model for inventory table.
"""

from typing import Any

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable


class InventoryTable(BaseTable):
    """Inventory Table."""

    item_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"))
    minimum_stock_level: Mapped[int] = mapped_column(Integer)
    supplier = relationship("SupplierTable", back_populates="inventory_items")
    transactions = relationship(
        "StockTransactionTable", back_populates="inventory"
    )
