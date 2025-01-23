"""Customer Model.

Description:
- This module contains model for Customer table.

"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable


class CustomerTable(BaseTable):
    """Customer Table."""

    name: Mapped[str] = mapped_column(String(2_55))
    mobile_number: Mapped[str] = mapped_column(String(20))
    vehicle_registration_number: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)

    # Relationships
    vehicles = relationship("VehicleTable", back_populates="customer")
