"""StockTransaction Models.

Description:
- This module contains model for stocktransaction table.
"""

from datetime import datetime

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.jobcard.model import JobCard


class StockTransaction(Base, table=True):
    """Stock Transaction Table."""

    id: int = Field(primary_key=True, index=True)
    inventory_id: int = Field(foreign_key="inventory.id")
    transaction_type: str = Field(max_length=50)
    quantity: int
    transaction_date: datetime
    job_card_id: int | None = Field(foreign_key="jobcard.id")
    remarks: str = Field()

    inventory: Inventory = Relationship(back_populates="transactions")
    job_card: JobCard = Relationship(back_populates="transactions")
