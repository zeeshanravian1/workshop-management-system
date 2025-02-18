"""Association tables for Inventory relationships."""

from sqlmodel import Field, SQLModel


class InventoryEstimate(SQLModel, table=True):
    """Association table for Inventory-Estimate relationship."""

    inventory_id: int = Field(foreign_key="inventory.id", primary_key=True)
    estimate_id: int = Field(foreign_key="estimate.id", primary_key=True)
    quantity_used: int
    unit_price_at_time: float = Field(max_digits=10, decimal_places=2)
