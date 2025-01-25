"""Notification Models.

Description:
- This module contains model for notification table.
"""

from datetime import datetime
from uuid import UUID

from sqlmodel import DateTime, Field

from workshop_management_system.database.connection import Base


class Notification(Base, table=True):
    """Notification Table."""

    customer_id: UUID = Field(foreign_key="customer.id")
    message: str
    status: str = Field(max_length=50)
    notification_date: datetime = Field(
        default_factory=DateTime, nullable=False
    )
