from typing import List, Optional, TYPE_CHECKING

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from workshop_management_system.database.connection import Base

if TYPE_CHECKING:
    from workshop_management_system.v1.inventory.model import Inventory


class Supplier(Base, table=True):
    """Supplier Table."""

    supplier_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    inventory_items: List["Inventory"] = Relationship(
        back_populates="supplier"
    )
