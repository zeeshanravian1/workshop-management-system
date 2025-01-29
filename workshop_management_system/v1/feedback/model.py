"""FeedBack Models.

Description:
- This module contains model for feedback table.

"""

from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.customer.model import Customer


class FeedBack(Base, table=True):
    """FeedBack Table."""

    description: str = Field()
    status: str = Field(max_length=50)
    customer_id: UUID = Field(foreign_key="customer.id")
    customer: list["Customer"] = Relationship(back_populates="complaints")
