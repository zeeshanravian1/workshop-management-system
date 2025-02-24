"""JobCard Model.

Description:
- This module contains model for job card table.

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
from workshop_management_system.v1.inventory_jobcard_link.model import (
    InventoryJobCardLink,
)
from workshop_management_system.v1.vehicle.model import Vehicle


class JobCardBase(SQLModel):
    """JobCard Base Table.

    Description:
    - This class contains base model for job card table.

    :Attributes:
    - `status (ServiceStatus)`: Status of job card.
    - `service_date (date)`: Date of service.
    - `description (str)`: Description of job card.
    - `vehicle_id (int)`: Unique identifier for vehicle.

    """

    status: ServiceStatus
    service_date: date = Field(default_factory=date.today)
    description: str
    vehicle_id: int = Field(foreign_key="vehicle.id", ondelete="CASCADE")

    # Validators
    service_date_validator = field_validator("service_date")(date_validator)


class JobCard(Base, JobCardBase, table=True):
    """JobCard Table.

    Description:
    - This class contains model for job card table.

    :Attributes:
    - `id (int)`: Unique identifier for job card.
    - `status (ServiceStatus)`: Status of job card.
    - `service_date (date)`: Date of service.
    - `description (str)`: Description of job card.
    - `vehicle_id (int)`: Unique identifier for vehicle.
    - `created_at (datetime)`: Timestamp when job card was created.
    - `updated_at (datetime)`: Timestamp when job card was last updated.

    """

    vehicle: Vehicle = Relationship(back_populates="job_cards")
    inventories: list[Inventory] = Relationship(
        back_populates="jobcards", link_model=InventoryJobCardLink
    )
