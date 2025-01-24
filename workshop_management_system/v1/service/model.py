"""Service Models.

Description:
- This module contains model for service table.
"""

from typing import Any

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.jobcard.model import JobCardTable


class ServiceTable(BaseTable):
    """Service Table."""

    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    service_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    cost: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    job_card: Mapped["JobCardTable"] = relationship(back_populates="services")
