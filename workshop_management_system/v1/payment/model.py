"""Payment Models.

Description:
- This module contains model for payment table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base
from workshop_management_system.v1.customer.model import Customer

if TYPE_CHECKING:
    from workshop_management_system.v1.jobcard.model import JobCard


class Payment(Base, table=True):
    """Payment Table."""

    customer_id: int = Field(foreign_key="customer.id")
    job_card_id: int = Field(foreign_key="jobcard.id")
    amount: float = Field(max_digits=10, decimal_places=2)
    credit: float = Field(max_digits=10, decimal_places=2)
    balance: float = Field(max_digits=10, decimal_places=2)
    payment_date: datetime
    payment_method: str = Field(max_length=50)
    reference_number: str = Field(max_length=100)
    status: str = Field(max_length=50)

    customer: Customer = Relationship(back_populates="payments")
    job_card: "JobCard" = Relationship(back_populates="payments")
