"""JobCard repository for CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import JobCardTable


class JobCardRepository:
    """JobCard repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, jobcard_data: dict) -> JobCardTable:
        """Create new job card."""
        try:
            jobcard = JobCardTable(
                customer_id=jobcard_data["customer_id"],
                vehicle_id=jobcard_data["vehicle_id"],
                service_date=jobcard_data["service_date"],
                status=jobcard_data["status"],
                total_amount=jobcard_data["total_amount"],
                supervisor_id=jobcard_data["supervisor_id"],
                mechanic_id=jobcard_data["mechanic_id"],
                nhil=jobcard_data.get("nhil", 2.5),
                getfund=jobcard_data.get("getfund", 2.5),
                covid_levy=jobcard_data.get("covid_levy", 1.0),
                total_levy=jobcard_data.get("total_levy", 0),
                vat=jobcard_data.get("vat", 15.0),
                total_inclusive_tax=jobcard_data.get("total_inclusive_tax", 0),
            )
            self.session.add(jobcard)
            await self.session.commit()
            await self.session.refresh(jobcard)
            return jobcard
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error creating job card: {e!s}")

    async def get_by_id(self, jobcard_id: int) -> JobCardTable | None:
        """Get job card by ID."""
        try:
            query = select(JobCardTable).where(JobCardTable.id == jobcard_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Error fetching job card: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[JobCardTable]:
        """Get all job cards with pagination."""
        try:
            query = select(JobCardTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise Exception(f"Error fetching job cards: {e!s}")

    async def update(
        self, jobcard_id: int, update_data: dict
    ) -> JobCardTable | None:
        """Update job card details."""
        try:
            jobcard = await self.get_by_id(jobcard_id)
            if jobcard:
                for key, value in update_data.items():
                    setattr(jobcard, key, value)
                await self.session.commit()
                await self.session.refresh(jobcard)
            return jobcard
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating job card: {e!s}")

    async def delete(self, jobcard_id: int) -> bool:
        """Delete job card."""
        try:
            jobcard = await self.get_by_id(jobcard_id)
            if jobcard:
                await self.session.delete(jobcard)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error deleting job card: {e!s}")
