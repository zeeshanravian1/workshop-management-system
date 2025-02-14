"""Supplier Model.

Description:
- This module contains model for supplier table.

"""

from typing import TYPE_CHECKING

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.inventory_supplier_link.model import (
    InventorySupplierLink,
)

if TYPE_CHECKING:
    from workshop_management_system.v1.inventory.model import Inventory


class SupplierBase(SQLModel):
    """Supplier Base Table.

    Description:
    - This class contains base model for Supplier table.

    :Attributes:
    - `name (str)`: Name of supplier.
    - `email (str)`: Email of supplier.
    - `contact_no (str)`: Contact number of supplier.
    - `address (str)`: Address of supplier.

    """

    name: str = Field(max_length=255)
    email: EmailStr | None = Field(
        max_length=255, unique=True, nullable=True, index=True
    )
    contact_no: PhoneNumber = Field(max_length=255, unique=True, index=True)
    address: str | None = Field(max_length=255, nullable=True)


class Supplier(Base, SupplierBase, table=True):
    """Supplier Table.

    Description:
    - This class contains model for Supplier table.

    :Attributes:
    - `id (int)`: Unique identifier for supplier.
    - `name (str)`: Name of supplier.
    - `email (str)`: Email of supplier.
    - `contact_no (str)`: Contact number of supplier.
    - `address (str)`: Address of supplier.
    - `created_at (datetime)`: Timestamp when supplier was created.
    - `updated_at (datetime)`: Timestamp when supplier was last updated.

    """

    inventories: list["Inventory"] = Relationship(
        back_populates="suppliers", link_model=InventorySupplierLink
    )
