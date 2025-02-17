"""Complaint Models."""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from ..customer.model import Customer


class Complaint(Base, table=True):
    """Complaint Table."""

    description: str = Field()
    status: str = Field(max_length=50)
    priority: str = Field(max_length=50)
    customer_id: int | None = Field(foreign_key="customer.id")

    customer: Optional["Customer"] = Relationship(back_populates="complaints")
