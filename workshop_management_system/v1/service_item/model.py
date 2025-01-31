"""ServiceItem Model.

Description:
- This module contains model for serviceitem table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.inventory.model import Inventory
    from workshop_management_system.v1.jobcard.model import JobCard


class ServiceItem(Base, table=True):
    """Service Item Table."""

    job_card_id: int = Field(foreign_key="jobcard.id")
    inventory_id: int = Field(foreign_key="inventory.id")
    item_name: str = Field(max_length=255)
    item_description: str = Field(default=None)
    quantity: int
    unit_price: float
    discount: float
    total_amount: float

    job_card: "JobCard" = Relationship(back_populates="service_items")
    inventory: "Inventory" = Relationship(back_populates="service_items")
