"""JobCard Model.

Description:
- This module contains model for jobcard table.

"""

from datetime import datetime

from sqlalchemy import DateTime, Decimal, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable


class JobCardTable(BaseTable):
    """Job Card Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    service_date: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50))
    total_amount: Mapped[Decimal] = mapped_column(Decimal(10, 2))
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    mechanic_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))

    customer = relationship("CustomerTable", back_populates="job_cards")
    vehicle = relationship("VehicleTable", back_populates="job_cards")
    supervisor = relationship(
        "EmployeeTable",
        foreign_keys=[supervisor_id],
        back_populates="supervised_jobs",
    )
    mechanic = relationship(
        "EmployeeTable",
        foreign_keys=[mechanic_id],
        back_populates="mechanic_jobs",
    )
    services = relationship("ServiceTable", back_populates="job_card")
    service_items = relationship("ServiceItemTable", back_populates="job_card")
