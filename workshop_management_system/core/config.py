"""Core Configuration Module.

Description:
- This module is responsible for core configuration.

"""

from datetime import date
from enum import Enum

DATABASE_URL: str = "sqlite:///database.db"


class InventoryCategory(str, Enum):
    """Inventory Category Enum.

    Description:
    - This class contains enum for inventory category.

    """

    LUBRICANTS = "lubricants"
    ELECTRICALS = "electricals"
    SPARE_PARTS = "spare_parts"
    TOOLS = "tools"
    OTHERS = "others"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Choices Method.

        Description:
        - This method is used to get choices for enum.

        :Args:
        - `None`

        :Returns:
        - `list[tuple[str, str]]`: List of choices for enum.

        """
        return [(key.value, key.name) for key in cls]

    @classmethod
    def get_comma_separated_categories(cls) -> str:
        """Get Comma Separated Categories Method.

        Description:
        - This method is used to get comma separated categories.

        :Args:
        - `None`

        :Returns:
        - `str`: Comma separated categories.

        """
        return ", ".join([key.value for key in cls])


class ServiceStatus(str, Enum):
    """Service Status Enum.

    Description:
    - This class contains enum for service status.

    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Choices Method.

        Description:
        - This method is used to get choices for enum.

        :Args:
        - `None`

        :Returns:
        - `list[tuple[str, str]]`: List of choices for enum.

        """
        return [(key.value, key.name) for key in cls]

    @classmethod
    def get_comma_separated_statuses(cls) -> str:
        """Get Comma Separated Statuses Method.

        Description:
        - This method is used to get comma separated statuses.

        :Args:
        - `None`

        :Returns:
        - `str`: Comma separated statuses.

        """
        return ", ".join([key.value for key in cls])


def service_date_validator(service_date: date) -> date:
    """Service Date Validator.

    Description:
    - This function is used to validate service date.

    :Args:
    - `v (date)`: Service date.

    :Returns:
    - `date`: Service date.

    """
    if service_date < date.today():
        raise ValueError("Service date cannot be in the past")

    return service_date
