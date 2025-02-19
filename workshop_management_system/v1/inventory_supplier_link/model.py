"""Inventory Supplier Link Model.

Description:
- This module contains model for inventory supplier link table.

"""

from sqlmodel import Field, SQLModel


class InventorySupplierLink(SQLModel, table=True):
    """Inventory Supplier Link Table.

    Description:
    - This class contains model for inventory supplier link table.
    - This table is used to link inventory and supplier tables.

    :Attributes:
    - `inventory_id (int)`: Unique identifier for inventory.
    - `supplier_id (int)`: Unique identifier for supplier.

    """

    inventory_id: int = Field(
        foreign_key="inventory.id", primary_key=True, ondelete="CASCADE"
    )
    supplier_id: int = Field(
        foreign_key="supplier.id", primary_key=True, ondelete="CASCADE"
    )
