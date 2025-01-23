"""CRUD operations for complaint."""
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .model import ComplaintTable


class ComplaintRepository:
    """Complaint repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, complaint_data: dict) -> ComplaintTable:
        """Create a new complaint."""
        try:
            complaint = ComplaintTable(
                customer_id=complaint_data["customer_id"],
                description=complaint_data["description"],
                status=complaint_data["status"],
            )
            self.session.add(complaint)
            await self.session.commit()
            await self.session.refresh(complaint)
            return complaint
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error creating complaint: {e!s}")

    async def get_by_id(self, complaint_id: int) -> ComplaintTable | None:
        """Get a complaint by ID."""
        try:
            query = select(ComplaintTable).where(
                ComplaintTable.id == complaint_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise SQLAlchemyError(f"Error fetching complaint: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[ComplaintTable]:
        """Get all complaints with pagination."""
        try:
            query = select(ComplaintTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLAlchemyError(f"Error fetching complaints: {e!s}")

    async def update(
        self, complaint_id: int, complaint_data: dict
    ) -> ComplaintTable:
        """Update a complaint by ID."""
        try:
            complaint = await self.get_by_id(complaint_id)
            if not complaint:
                raise ValueError("Complaint not found")
            for key, value in complaint_data.items():
                setattr(complaint, key, value)
            await self.session.commit()
            await self.session.refresh(complaint)
            return complaint
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error updating complaint: {e!s}")

    async def delete(self, complaint_id: int) -> ComplaintTable:
        """Delete a complaint by ID."""
        try:
            complaint = await self.get_by_id(complaint_id)
            if not complaint:
                raise ValueError("Complaint not found")
            await self.session.delete(complaint)
            await self.session.commit()
            return complaint
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error deleting complaint: {e!s}")
