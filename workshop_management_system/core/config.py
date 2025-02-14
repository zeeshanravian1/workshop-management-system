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
    SPARE_PARTS = "spare_parts"
    TOOLS = "tools"
    OTHERS = "others"
