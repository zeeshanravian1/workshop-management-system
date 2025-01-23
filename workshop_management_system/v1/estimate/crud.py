"""Estimate repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import EstimateTable


class EstimateRepository:
    """Estimate repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, estimate_data: dict) -> EstimateTable:
        """Create new estimate."""
        try:
            estimate = EstimateTable(
                customer_id=estimate_data["customer_id"],
                vehicle_id=estimate_data["vehicle_id"],
                estimate_date=datetime.now(),
                total_estimate_amount=estimate_data["total_estimate_amount"],
                status="pending",
                nhil=estimate_data.get("nhil", 0),
                getfund=estimate_data.get("getfund", 0),
                covid_levy=estimate_data.get("covid_levy", 0),
                total_levy=estimate_data.get("total_levy", 0),
                vat=estimate_data.get("vat", 0),
                total_inclusive_tax=estimate_data.get(
                    "total_inclusive_tax", 0),
            )
            self.session.add(estimate)
            await self.session.commit()
            await self.session.refresh(estimate)
            return estimate
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error creating estimate: {e!s}")

    async def get_by_id(self, estimate_id: int) -> EstimateTable | None:
        """Get estimate by ID."""
        try:
            query = select(EstimateTable).where(
                EstimateTable.id == estimate_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Error fetching estimate: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[EstimateTable]:
        """Get all estimates with pagination."""
        try:
            query = select(EstimateTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise Exception(f"Error fetching estimates: {e!s}")

    async def update(
        self, estimate_id: int, update_data: dict
    ) -> EstimateTable | None:
        """Update estimate."""
        try:
            estimate = await self.get_by_id(estimate_id)
            if estimate:
                for key, value in update_data.items():
                    setattr(estimate, key, value)
                await self.session.commit()
                await self.session.refresh(estimate)
            return estimate
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating estimate: {e!s}")

    async def delete(self, estimate_id: int) -> bool:
        """Delete estimate."""
        try:
            estimate = await self.get_by_id(estimate_id)
            if estimate:
                await self.session.delete(estimate)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error deleting estimate: {e!s}")
