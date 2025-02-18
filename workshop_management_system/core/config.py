"""Core Configuration Module.

Description:
- This module is responsible for core configuration.

"""

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
