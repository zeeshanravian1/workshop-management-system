"""Inventory Models.

Description:
- This module contains model for inventory table.
"""

from sqlalchemy import Decimal, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.stocktransaction.model import (
    StockTransactionTable,
)
from workshop_management_system.supplier.model import SupplierTable


class InventoryTable(BaseTable):
    """Inventory Table."""

    item_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"))
    minimum_stock_level: Mapped[int] = mapped_column(Integer)
    supplier: Mapped["SupplierTable"] = relationship(
        back_populates="inventory_items"
    )
    transactions: Mapped[list["StockTransactionTable"]] = relationship(
        back_populates="inventory"
    )
