"""Inventory Model.

Description:
- This module contains model for inventory table.

"""

from pydantic import PrivateAttr
from sqlmodel import Field, Relationship, SQLModel

from workshop_management_system.core.config import (
    INVENTORY_MINIMUM_THRESHOLD,
    InventoryCategory,
)
from workshop_management_system.database.connection import Base
from workshop_management_system.v1.inventory_jobcard_link.model import (
    InventoryJobCardLink,
)
from workshop_management_system.v1.inventory_service_link.model import (
    InventoryServiceLink,
)
from workshop_management_system.v1.inventory_supplier_link.model import (
    InventorySupplierLink,
)
from workshop_management_system.v1.supplier.model import Supplier


class InventoryBase(SQLModel):
    """Inventory Base Table.

    Description:
    - This class contains base model for Inventory table.

    :Attributes:
    - `item_name (str)`: Name of item.
    - `quantity (int)`: Quantity of item.
    - `unit_price (float)`: Price of item per unit.
    - `minimum_threshold (int)`: Minimum threshold for item.
    - `category (InventoryCategory)`: Category of item.

    """

    item_name: str = Field(max_length=255, unique=True, index=True)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    minimum_threshold: int = Field(default=INVENTORY_MINIMUM_THRESHOLD, gt=0)
    category: InventoryCategory = Field(default=InventoryCategory.OTHERS)


class Inventory(Base, InventoryBase, table=True):
    """Inventory Table.

    Description:
    - This class contains model for Inventory table.

    :Attributes:
    - `id (int)`: Unique identifier for inventory.
    - `item_name (str)`: Name of item.
    - `quantity (int)`: Quantity of item.
    - `unit_price (float)`: Price of item per unit.
    - `minimum_threshold (int)`: Minimum threshold for item.
    - `category (InventoryCategory)`: Category of item.
    - `service_quantity (int)`: Quantity of item used in service.
    - `created_at (datetime)`: Timestamp when inventory was created.
    - `updated_at (datetime)`: Timestamp when inventory was last updated.

    """

    _service_quantity: int = PrivateAttr(default=1)

    suppliers: list[Supplier] = Relationship(
        back_populates="inventories", link_model=InventorySupplierLink
    )
    jobcards: list["JobCard"] = Relationship(  # type: ignore # noqa: F821
        back_populates="inventories", link_model=InventoryJobCardLink
    )
    services: list["Service"] = Relationship(  # type: ignore # noqa: F821
        back_populates="inventories", link_model=InventoryServiceLink
    )
