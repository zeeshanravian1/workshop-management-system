"""CRUD operations for Supplier."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import SupplierTable


class SupplierRepository:
    """Supplier repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, supplier_data: dict) -> SupplierTable:
        """Create new supplier."""
        try:
            supplier = SupplierTable(
                name=supplier_data["name"],
                contact_number=supplier_data["contact_number"],
                address=supplier_data["address"],
            )
            self.session.add(supplier)
            await self.session.commit()
            await self.session.refresh(supplier)
            return supplier
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error creating supplier: {e!s}")

    async def get_by_id(self, supplier_id: int) -> SupplierTable | None:
        """Get supplier by ID with related data."""
        try:
            query = (
                select(SupplierTable)
                .where(SupplierTable.id == supplier_id)
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Error fetching supplier: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[SupplierTable]:
        """Get all suppliers with pagination."""
        try:
            query = select(SupplierTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise Exception(f"Error fetching suppliers: {e!s}")

    async def update(
        self, supplier_id: int, supplier_data: dict
    ) -> SupplierTable:
        """Update supplier by ID."""
        try:
            supplier = await self.get_by_id(supplier_id)
            if not supplier:
                raise Exception("Supplier not found")
            for key, value in supplier_data.items():
                setattr(supplier, key, value)
            await self.session.commit()
            await self.session.refresh(supplier)
            return supplier
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating supplier: {e!s}")

    async def delete(self, supplier_id: int) -> SupplierTable:
        """Delete supplier by ID."""
        try:
            supplier = await self.get_by_id(supplier_id)
            if not supplier:
                raise Exception("Supplier not found")
            await self.session.delete(supplier)
            await self.session.commit()
            return supplier
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error deleting supplier: {e!s}")
