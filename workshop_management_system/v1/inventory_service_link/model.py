"""Inventory Service Link Model.

Description:
- This module contains model for inventory service link table.

"""

from sqlmodel import Field, SQLModel


class InventoryServiceLink(SQLModel, table=True):
    """Inventory Service Link Table.

    Description:
    - This class contains model for inventory service link table.
    - This table is used to link inventory and service tables.

    :Attributes:
    - `inventory_id (int)`: Unique identifier for inventory.
    - `service_id (int)`: Unique identifier for service.

    """

    inventory_id: int = Field(
        foreign_key="inventory.id", primary_key=True, ondelete="CASCADE"
    )
    service_id: int = Field(
        foreign_key="service.id", primary_key=True, ondelete="CASCADE"
    )
