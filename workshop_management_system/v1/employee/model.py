"""Employee Models.

Description:
- This module contains model for Employee table.
"""

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base


class Employee(Base, table=True):
    """Employee Table."""

    name: str = Field(max_length=255)
    username: str = Field(max_length=255, unique=True)
    email: str = Field(max_length=255, unique=True)
    password: str = Field(max_length=255)
    role: str = Field(max_length=50)
    is_active: bool = Field(default=True)

    supervised_jobs: list["JobCard"] = Relationship(  # type: ignore
        back_populates="supervisor",
        sa_relationship_kwargs={"foreign_keys": "JobCardTable.supervisor_id"},
    )
    mechanic_jobs: list["JobCard"] = Relationship(  # type: ignore
        back_populates="mechanic",
        sa_relationship_kwargs={"foreign_keys": "JobCardTable.mechanic_id"},
    )
    # electrician_jobs: list["JobCardTable"] = Relationship(  # type: ignore
    #     back_populates="electrician",
    #     sa_relationship_kwargs={"foreign_keys": "JobCardTable.electrician_id"}
    # )
