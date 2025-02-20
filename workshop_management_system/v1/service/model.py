"""Service Model.

Description:
- This module contains model for service table.

"""

from datetime import date

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.core.config import (
    ServiceStatus,
    date_validator,
)
from workshop_management_system.database.connection import Base
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory_service_link.model import (
    InventoryServiceLink,
)
from workshop_management_system.v1.vehicle.model import Vehicle


class ServiceBase(SQLModel):
    """Service Base Table.

    Description:
    - This class contains base model for service table.

    :Attributes:
    - `status (ServiceStatus)`: Status of the job card.
    - `service_date (date)`: Date of service.
    - `delivery_date (date)`: Date of delivery.
    - `description (str)`: Description of the job card.
    - `vehicle_id (int)`: Unique identifier for vehicle.

    """

    status: ServiceStatus
    service_date: date = Field(default_factory=date.today)
    delivery_date: date = Field(default_factory=date.today)
    description: str
    vehicle_id: int = Field(foreign_key="vehicle.id", ondelete="CASCADE")

    # Validators
    service_date_validator = field_validator("service_date")(date_validator)
    delivery_date_validator = field_validator("delivery_date")(date_validator)


class Service(Base, ServiceBase, table=True):
    """Service Table.

    Description:
    - This class contains model for service table.

    :Attributes:
    - `id (int)`: Unique identifier for service.
    - `status (ServiceStatus)`: Status of the job card.
    - `service_date (date)`: Date of service.
    - `delivery_date (date)`: Date of delivery.
    - `description (str)`: Description of the job card.
    - `vehicle_id (int)`: Unique identifier for vehicle.
    - `created_at (datetime)`: Timestamp when job card was created.
    - `updated_at (datetime)`: Timestamp when job card was last updated.

    """

    vehicle: Vehicle = Relationship(back_populates="services")
    inventories: list[Inventory] = Relationship(
        back_populates="services", link_model=InventoryServiceLink
    )
