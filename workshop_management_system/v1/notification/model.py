"""Notification Models.

Description:
- This module contains model for notification table.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from workshop_management_system.database.connection import BaseTable


class NotificationTable(BaseTable):
    """Notification Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    notification_date: Mapped[datetime] = mapped_column(DateTime)
