"""User Model.

Description:
- This module contains model for user table.

"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workshop_management_system.database.connection import BaseTable


class EmployeeTable(BaseTable):
    """Employee Table.

    Description:
    - This table is used to create user in database.

    """

    name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    supervised_jobs = relationship(
        "JobCardTable",
        foreign_keys="JobCardTable.supervisor_id",
        back_populates="supervisor",
    )
    mechanic_jobs = relationship(
        "JobCardTable",
        foreign_keys="JobCardTable.mechanic_id",
        back_populates="mechanic",
    )
