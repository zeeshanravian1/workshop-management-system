"""CRUD operations for Employee."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import EmployeeTable


class EmployeeRepository:
    """Employee repository for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with session."""
        self.session = session

    async def create(self, employee_data: dict) -> EmployeeTable:
        """Create new employee."""
        try:
            employee = EmployeeTable(
                first_name=employee_data["first_name"],
                last_name=employee_data["last_name"],
                email=employee_data["email"],
                contact_number=employee_data["contact_number"],
                address=employee_data["address"],
                role=employee_data["role"],
            )
            self.session.add(employee)
            await self.session.commit()
            await self.session.refresh(employee)
            return employee
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error creating employee: {e!s}")

    async def get_by_id(self, employee_id: int) -> EmployeeTable | None:
        """Get employee by ID with related data."""
        try:
            query = (
                select(EmployeeTable)
                .where(EmployeeTable.id == employee_id)
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Error fetching employee: {e!s}")

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[EmployeeTable]:
        """Get all employees with pagination."""
        try:
            query = select(EmployeeTable).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise Exception(f"Error fetching employees: {e!s}")

    async def update(
        self, employee_id: int, employee_data: dict
    ) -> EmployeeTable:
        """Update employee by ID."""
        try:
            employee = await self.get_by_id(employee_id)
            if not employee:
                raise Exception("Employee not found.")
            for key, value in employee_data.items():
                setattr(employee, key, value)
            await self.session.commit()
            await self.session.refresh(employee)
            return employee
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating employee: {e!s}")

    async def delete(self, employee_id: int) -> bool:
        """Delete employee by ID."""
        try:
            employee = await self.get_by_id(employee_id)
            if not employee:
                raise Exception("Employee not found.")
            await self.session.delete(employee)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error deleting employee: {e!s}")
