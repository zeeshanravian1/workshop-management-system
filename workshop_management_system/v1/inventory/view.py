"""Inventory View Module.

Description:
- This module contains inventory view for inventory model.

"""

from ..base.view import BaseView
from .model import Inventory


class InventoryView(BaseView[Inventory]):
    """Inventory View Class.

    Description:
    - This class provides CRUD interface for inventory model.

    """
