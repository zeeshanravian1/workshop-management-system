"""Payment Models.

Description:
- This module contains model for payment table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.v1.customer.model import Customer

if TYPE_CHECKING:
    from workshop_management_system.v1.jobcard.model import JobCard


class Payment(SQLModel, table=True):
    """Payment Table."""

    payment_id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    job_card_id: int = Field(foreign_key="jobcard.id")
    amount: float = Field(max_digits=10, decimal_places=2)
    payment_date: datetime
    payment_method: str = Field(max_length=50)
    reference_number: str = Field(max_length=100)
    status: str = Field(max_length=50)

    customer: Customer = Relationship(back_populates="payments")
    job_card: "JobCard" = Relationship(back_populates="payments")
