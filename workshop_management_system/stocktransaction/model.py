"""StockTransaction Models.

Description:
- This module contains model for stocktransaction table.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.inventory.model import InventoryTable


class StockTransactionTable(BaseTable):
    """Stock Transaction Table."""

    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"))
    transaction_type: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer)
    transaction_date: Mapped[datetime] = mapped_column(DateTime)
    job_card_id: Mapped[int | None] = mapped_column(ForeignKey("jobcard.id"))
    remarks: Mapped[str] = mapped_column(Text)
    inventory: Mapped["InventoryTable"] = relationship(
        back_populates="transactions"
    )
