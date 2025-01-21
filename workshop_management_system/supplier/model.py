"""Supplier Models.

Description:
- This module contains model for supplier table.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.inventory.model import InventoryTable


class SupplierTable(BaseTable):
    """Supplier Table."""

    name: Mapped[str] = mapped_column(String(255))
    contact_number: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(Text)
    inventory_items: Mapped[list["InventoryTable"]] = relationship(
        back_populates="supplier"
    )
