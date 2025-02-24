"""Inventory JobCard Link Model.

Description:
- This module contains model for inventory job card link table.

"""

from sqlmodel import Field, SQLModel


class InventoryJobCardLink(SQLModel, table=True):
    """Inventory JobCard Link Table.

    Description:
    - This class contains model for inventory job card link table.
    - This table is used to link inventory and job card tables.

    :Attributes:
    - `inventory_id (int)`: Unique identifier for inventory.
    - `job_card_id (int)`: Unique identifier for job card.

    """

    inventory_id: int = Field(
        foreign_key="inventory.id", primary_key=True, ondelete="CASCADE"
    )
    jobcard_id: int = Field(
        foreign_key="jobcard.id", primary_key=True, ondelete="CASCADE"
    )
    quantity: int = Field(default=1, gt=0)
