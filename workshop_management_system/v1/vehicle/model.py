"""Vehicle Model.

Description:
- This module contains model for vehicle table.

"""

from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.customer.model import Customer


class VehicleBase(SQLModel):
    """Vehicle Base Table.

    Description:
    - This class contains base model for vehicle table.

    :Attributes:
    - `make (str)`: Make of the vehicle.
    - `model (str)`: Model of the vehicle.
    - `year (int)`: Year of manufacture.
    - `vehicle_number (str)`: Vehicle Identification Number.
    - `customer_id (int)`: Unique identifier for customer.

    """

    make: str = Field(max_length=255)
    model: str = Field(max_length=255)
    year: int = Field(ge=1886)
    vehicle_number: str = Field(max_length=17, unique=True, index=True)
    customer_id: int = Field(foreign_key="customer.id", ondelete="CASCADE")


class Vehicle(Base, VehicleBase, table=True):
    """Vehicle Table.

    Description:
    - This class contains model for vehicle table.

    :Attributes:
    - `id (int)`: Unique identifier for vehicle.
    - `make (str)`: Make of the vehicle.
    - `model (str)`: Model of the vehicle.
    - `year (int)`: Year of manufacture.
    - `vehicle_number (str)`: Vehicle Identification Number.
    - `customer_id (int)`: Unique identifier for customer.
    - `created_at (datetime)`: Timestamp when vehicle was created.
    - `updated_at (datetime)`: Timestamp when vehicle was last updated.

    """

    customer: Customer = Relationship(back_populates="vehicles")
    job_cards: list["JobCard"] = Relationship(  # type: ignore # noqa: F821
        back_populates="vehicle", cascade_delete=True
    )
