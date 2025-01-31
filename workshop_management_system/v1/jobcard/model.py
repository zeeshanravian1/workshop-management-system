"""JobCard Model.

Description:
- This module contains model for jobcard table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.payment.model import Payment
    from workshop_management_system.v1.service.model import Service
    from workshop_management_system.v1.service_item.model import ServiceItem
    from workshop_management_system.v1.stock_transaction.model import (
        StockTransaction,
    )
    from workshop_management_system.v1.vehicle.model import Vehicle


class JobCard(Base, table=True):
    """Job Card Table."""

    vehicle_id: int = Field(foreign_key="vehicle.id")
    service_date: datetime
    status: str = Field(max_length=50)
    total_amount: float = Field(max_digits=10, decimal_places=2)
    description: str = Field(max_length=300)

    vehicle: "Vehicle" = Relationship(back_populates="job_cards")

    services: list["Service"] = Relationship(back_populates="job_card")
    service_items: list["ServiceItem"] = Relationship(
        back_populates="job_card"
    )
    payments: list["Payment"] = Relationship(back_populates="job_card")
    transactions: list["StockTransaction"] = Relationship(
        back_populates="job_card"
    )
