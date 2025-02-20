"""Customer Model.

Description:
- This module contains model for customer table.

"""

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.database.connection import Base


class CustomerBase(SQLModel):
    """Customer Base Table.

    Description:
    - This class contains base model for customer table.

    :Attributes:
    - `name (str)`: Name of customer.
    - `email (str)`: Email of customer.
    - `contact_no (str)`: Contact number of customer.
    - `address (str)`: Address of customer.

    """

    name: str = Field(max_length=255)
    email: EmailStr | None = Field(
        max_length=255, unique=True, nullable=True, index=True
    )
    contact_no: PhoneNumber = Field(max_length=255, unique=True, index=True)
    address: str | None = Field(max_length=255, nullable=True)


class Customer(Base, CustomerBase, table=True):
    """Customer Table.

    Description:
    - This class contains model for customer table.

    :Attributes:
    - `id (int)`: Unique identifier for customer.
    - `name (str)`: Name of customer.
    - `email (str)`: Email of customer.
    - `contact_no (str)`: Contact number of customer.
    - `address (str)`: Address of customer.
    - `created_at (datetime)`: Timestamp when customer was created.
    - `updated_at (datetime)`: Timestamp when customer was last updated.

    """

    vehicles: list["Vehicle"] = Relationship(  # type: ignore # noqa: F821
        back_populates="customer", cascade_delete=True
    )
    estimates: list["Estimate"] = Relationship(back_populates="customer")
    complaints: list["Complaint"] = Relationship(back_populates="customer")
    payments: list["Payment"] = Relationship(back_populates="customer")
