"""FeedBack Models.

Description:
- This module contains model for feedback table.

"""

# from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from ..customer.model import Customer
    from ..employee.model import Employee


# from workshop_management_system.v1.customer.model import Customer


class FeedBack(Base, table=True):
    """FeedBack Table."""

    description: str = Field()
    status: str = Field(max_length=50)
    customer_id: int = Field(foreign_key="customer.id")
    employee_id: int = Field(foreign_key="employee.id")

    customer: Optional["Customer"] = Relationship(back_populates="feedbacks")
    employee: Optional["Employee"] = Relationship(back_populates="feedbacks")
