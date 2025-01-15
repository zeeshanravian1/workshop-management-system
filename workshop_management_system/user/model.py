"""User Model.

Description:
- This module contains model for user table.

"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from workshop_management_system.database.connection import BaseTable


class UserTable(BaseTable):
    """User Table.

    Description:
    - This table is used to create user in database.

    """

    name: Mapped[str] = mapped_column(String(2_55))
    username: Mapped[str] = mapped_column(String(2_55), unique=True)
    email: Mapped[str] = mapped_column(String(2_55), unique=True)
    password: Mapped[str] = mapped_column(String(2_55))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
