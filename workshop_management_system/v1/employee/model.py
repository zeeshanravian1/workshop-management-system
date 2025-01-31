"""Employee Models.

Description:
- This module contains model for Employee table.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.feedback.model import FeedBack
    from workshop_management_system.v1.jobcard.model import JobCard
    from workshop_management_system.v1.service.model import Service


class Employee(Base, table=True):
    """Employee Table."""

    name: str = Field(max_length=255)
    username: str = Field(max_length=255, unique=True)
    email: str = Field(max_length=255, unique=True)
    password: str = Field(max_length=255)
    role: str = Field(max_length=50)
    is_active: bool = Field(default=True)

    feedbacks: list["FeedBack"] = Relationship(back_populates="employee")
    supervised_jobs: list["JobCard"] = Relationship(
        back_populates="supervisor",
        sa_relationship_kwargs={"foreign_keys": "JobCard.supervisor_id"},
    )
    mechanic_jobs: list["JobCard"] = Relationship(
        back_populates="mechanic",
        sa_relationship_kwargs={"foreign_keys": "JobCard.mechanic_id"},
    )
    services: list["Service"] = Relationship(back_populates="employee")
