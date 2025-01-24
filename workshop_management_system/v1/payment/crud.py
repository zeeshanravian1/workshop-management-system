"""CRUD operations for Payment."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import PaymentTable


class PaymentRepository:
    """Payment repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, payment_data: dict) -> PaymentTable:
        """Create a new payment."""
        try:
            payment = PaymentTable(
                customer_id=payment_data["customer_id"],
                job_card_id=payment_data["job_card_id"],
                amount=payment_data["amount"],
                payment_date=payment_data["payment_date"],
                payment_method=payment_data["payment_method"],
                reference_number=payment_data["reference_number"],
                status=payment_data["status"],
            )
            self.session.add(payment)
            await self.session.commit()
            await self.session.refresh(payment)
            return payment
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error creating payment: {e!s}")

    async def get_by_id(self, payment_id: int) -> PaymentTable | None:
        """Get a payment by ID."""
        try:
            query = select(PaymentTable).where(PaymentTable.id == payment_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise RuntimeError(f"Error fetching payment: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[PaymentTable]:
        """Get all payments with pagination."""
        try:
            query = select(PaymentTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise RuntimeError(f"Error fetching payments: {e!s}")

    async def update(
        self, payment_id: int, payment_data: dict
    ) -> PaymentTable:
        """Update a payment by ID."""
        try:
            payment = await self.get_by_id(payment_id)
            if not payment:
                raise ValueError("Payment not found")
            for key, value in payment_data.items():
                setattr(payment, key, value)
            await self.session.commit()
            await self.session.refresh(payment)
            return payment
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error updating payment: {e!s}")

    async def delete(self, payment_id: int) -> PaymentTable:
        """Delete a payment by ID."""
        try:
            payment = await self.get_by_id(payment_id)
            if not payment:
                raise ValueError("Payment not found")
            await self.session.delete(payment)
            await self.session.commit()
            return payment
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Error deleting payment: {e!s}")
