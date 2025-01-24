"""Customer Model.

Description:
- This module contains model for Customer table.

"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable


class CustomerTable(BaseTable):
    """Customer Table."""

<<<<<<< HEAD
    name: Mapped[str] = mapped_column(String(2_55))
=======
    name: Mapped[str] = mapped_column(String(255))
>>>>>>> fcc0fdcefbb8f3abbede91d8a8a5b920ae1ea766
    mobile_number: Mapped[str] = mapped_column(String(20))
    vehicle_registration_number: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)

<<<<<<< HEAD
    # Relationships
    vehicles = relationship("VehicleTable", back_populates="customer")
=======
    vehicles = relationship("VehicleTable", back_populates="customer")
    job_cards = relationship("JobCardTable", back_populates="customer")
    complaints = relationship("ComplaintTable", back_populates="customer")
    payments = relationship("PaymentTable", back_populates="customer")
>>>>>>> fcc0fdcefbb8f3abbede91d8a8a5b920ae1ea766
