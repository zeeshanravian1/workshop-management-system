"""CRUD operations for Notifications."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .model import NotificationTable


class NotificationRepository:
    """Notification repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, notification_data: dict) -> NotificationTable:
        """Create a new notification."""
        try:
            notification = NotificationTable(
                customer_id=notification_data["customer_id"],
                message=notification_data["message"],
                status=notification_data["status"],
                notification_date=notification_data["notification_date"],
            )
            self.session.add(notification)
            await self.session.commit()
            await self.session.refresh(notification)
            return notification
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error creating notification: {e!s}")

    async def get_by_id(
        self, notification_id: int
    ) -> NotificationTable | None:
        """Get a notification by ID."""
        try:
            query = select(NotificationTable).where(
                NotificationTable.id == notification_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise SQLAlchemyError(f"Error fetching notification: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[NotificationTable]:
        """Get all notifications with pagination."""
        try:
            query = select(NotificationTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLAlchemyError(f"Error fetching notifications: {e!s}")

    async def update(
        self, notification_id: int, notification_data: dict
    ) -> NotificationTable:
        """Update a notification by ID."""
        try:
            notification = await self.get_by_id(notification_id)
            if not notification:
                raise ValueError("Notification not found")
            for key, value in notification_data.items():
                setattr(notification, key, value)
            await self.session.commit()
            await self.session.refresh(notification)
            return notification
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error updating notification: {e!s}")

    async def delete(self, notification_id: int) -> NotificationTable:
        """Delete a notification by ID."""
        try:
            notification = await self.get_by_id(notification_id)
            if not notification:
                raise ValueError("Notification not found")
            await self.session.delete(notification)
            await self.session.commit()
            return notification
        except Exception as e:
            await self.session.rollback()
            raise SQLAlchemyError(f"Error deleting notification: {e!s}")
