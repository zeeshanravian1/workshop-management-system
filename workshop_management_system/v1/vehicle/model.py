"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable
<<<<<<< HEAD
from workshop_management_system.v1.customer.model import CustomerTable
=======
>>>>>>> fcc0fdcefbb8f3abbede91d8a8a5b920ae1ea766


class VehicleTable(BaseTable):
    """Vehicle Table."""

<<<<<<< HEAD
=======
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
>>>>>>> fcc0fdcefbb8f3abbede91d8a8a5b920ae1ea766
    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    chassis_number: Mapped[str] = mapped_column(String(50))
    engine_number: Mapped[str] = mapped_column(String(50))

<<<<<<< HEAD
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))

    # Relationships
    customer: Mapped[CustomerTable] = relationship(
        back_populates="vehicles", lazy="subquery"
    )
=======
    customer = relationship("CustomerTable", back_populates="vehicles")
    job_cards = relationship("JobCardTable", back_populates="vehicle")
    estimates = relationship("EstimateTable", back_populates="vehicle")
>>>>>>> fcc0fdcefbb8f3abbede91d8a8a5b920ae1ea766
