"""Notification Models.

Description:
- This module contains model for notification table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.customer.model import Customer


class Notification(Base, table=True):
    """Notification Table."""

    # notification_id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    message: str
    status: str = Field(max_length=50)
    notification_date: datetime = Field(
        default_factory=datetime.utcnow, nullable=False
    )

    # customer: "Customer" = Relationship(back_populates="notifications")
