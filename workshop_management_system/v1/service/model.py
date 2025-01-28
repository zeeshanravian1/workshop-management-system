"""Service Model.

Description:
- This module contains model for service table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.jobcard.model import JobCard


class Service(Base, table=True):
    """Service Table."""

    job_card_id: int = Field(foreign_key="jobcard.id")
    service_type: str = Field(max_length=100)
    description: str = Field()
    cost: float = Field()

    job_card: "JobCard" = Relationship(back_populates="services")
