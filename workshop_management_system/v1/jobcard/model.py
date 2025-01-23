"""JobCard Model.

Description:
- This module contains model for jobcard table.

"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn

from workshop_management_system.database.connection import BaseTable


class JobCardTable(BaseTable):
    """Job Card Table."""

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    service_date: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50))
    total_amount: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    mechanic_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))

    nhil: MappedColumn[Any] = mapped_column(Numeric(5, 2), default=2.5)
    getfund: MappedColumn[Any] = mapped_column(Numeric(5, 2), default=2.5)
    covid_levy: MappedColumn[Any] = mapped_column(Numeric(5, 2), default=1.0)
    total_levy: MappedColumn[Any] = mapped_column(Numeric(10, 2))
    vat: MappedColumn[Any] = mapped_column(Numeric(5, 2), default=15.0)
    total_inclusive_tax: MappedColumn[Any] = mapped_column(Numeric(10, 2))

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
