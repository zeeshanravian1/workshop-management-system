"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.customer.model import CustomerTable


class VehicleTable(BaseTable):
    """Vehicle Table."""

    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    chassis_number: Mapped[str] = mapped_column(String(50))
    engine_number: Mapped[str] = mapped_column(String(50))

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))

    # Relationships
    customer: Mapped[CustomerTable] = relationship(
        back_populates="vehicles", lazy="subquery"
    )
