"""CRUD operations for Inventory."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import InventoryTable


class InventoryRepository:
    """Inventory repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, inventory_data: dict) -> InventoryTable:
        """Create a new inventory item."""
        try:
            inventory_item = InventoryTable(
                item_name=inventory_data["item_name"],
                quantity=inventory_data["quantity"],
                unit_price=inventory_data["unit_price"],
                supplier_id=inventory_data["supplier_id"],
                minimum_stock_level=inventory_data["minimum_stock_level"],
            )
            self.session.add(inventory_item)
            await self.session.commit()
            await self.session.refresh(inventory_item)
            return inventory_item
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error creating inventory item: {e!s}")

    async def get_by_id(self, inventory_id: int) -> InventoryTable | None:
        """Get an inventory item by ID."""
        try:
            query = select(InventoryTable).where(
                InventoryTable.id == inventory_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise RuntimeError(f"Error fetching inventory item: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[InventoryTable]:
        """Get all inventory items with pagination."""
        try:
            query = select(InventoryTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise RuntimeError(f"Error fetching inventory items: {e!s}")

    async def update(
        self, inventory_id: int, inventory_data: dict
    ) -> InventoryTable:
        """Update an inventory item by ID."""
        try:
            inventory_item = await self.get_by_id(inventory_id)
            if not inventory_item:
                raise ValueError("Inventory item not found")
            for key, value in inventory_data.items():
                setattr(inventory_item, key, value)
            await self.session.commit()
            await self.session.refresh(inventory_item)
            return inventory_item
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error updating inventory item: {e!s}")

    async def delete(self, inventory_id: int) -> InventoryTable:
        """Delete an inventory item by ID."""
        try:
            inventory_item = await self.get_by_id(inventory_id)
            if not inventory_item:
                raise ValueError("Inventory item not found")
            await self.session.delete(inventory_item)
            await self.session.commit()
            return inventory_item
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Error deleting inventory item: {e!s}")
