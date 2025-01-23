"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable


class VehicleTable(BaseTable):
    """Vehicle Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    chassis_number: Mapped[str] = mapped_column(String(50))
    engine_number: Mapped[str] = mapped_column(String(50))

    customer = relationship("CustomerTable", back_populates="vehicles")
    job_cards = relationship("JobCardTable", back_populates="vehicle")
    estimates = relationship("EstimateTable", back_populates="vehicle")
