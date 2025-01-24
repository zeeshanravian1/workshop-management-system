"""Complaint Models.

Description:
- This module contains model for Complaint table.

"""

from uuid import UUID

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import BaseTable
from workshop_management_system.v1.customer.model import CustomerTable


class FeedBackTable(BaseTable, table=True):
    """Complaint Table."""

    description: str = Field()
    status: str = Field(max_length=50)
    customer_id: UUID = Field(foreign_key="customertable.id")
    customer: list["CustomerTable"] = Relationship(back_populates="complaints")
