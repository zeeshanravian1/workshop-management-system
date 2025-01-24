"""CRUD operations for Customer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import CustomerTable


class CustomerRepository:
    """Customer repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, customer_data: dict) -> CustomerTable:
        """Create a new customer."""
        try:
            customer = CustomerTable(
                name=customer_data["name"],
                mobile_number=customer_data["mobile_number"],
                vehicle_registration_number=customer_data[
                    "vehicle_registration_number"
                ],
                email=customer_data["email"],
                address=customer_data["address"],
            )
            self.session.add(customer)
            await self.session.commit()
            await self.session.refresh(customer)
            return customer
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error creating customer: {e!s}")

    async def get_by_id(self, customer_id: int) -> CustomerTable | None:
        """Get a customer by ID."""
        try:
            query = select(CustomerTable).where(
                CustomerTable.id == customer_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValueError(f"Error fetching customer: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[CustomerTable]:
        """Get all customers with pagination."""
        try:
            query = select(CustomerTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise ValueError(f"Error fetching customers: {e!s}")

    async def update(
        self, customer_id: int, customer_data: dict
    ) -> CustomerTable:
        """Update a customer by ID."""
        try:
            customer = await self.get_by_id(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            for key, value in customer_data.items():
                setattr(customer, key, value)
            await self.session.commit()
            await self.session.refresh(customer)
            return customer
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error updating customer: {e!s}")

    async def delete(self, customer_id: int) -> CustomerTable:
        """Delete a customer by ID."""
        try:
            customer = await self.get_by_id(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            await self.session.delete(customer)
            await self.session.commit()
            return customer
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error deleting customer: {e!s}")
