"""Service Models.

Description:
- This module contains model for service table.
"""

from sqlalchemy import Decimal, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.jobcard.model import JobCardTable


class ServiceTable(BaseTable):
    """Service Table."""

    job_card_id: Mapped[int] = mapped_column(ForeignKey("jobcard.id"))
    service_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    cost: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    job_card: Mapped["JobCardTable"] = relationship(back_populates="services")
