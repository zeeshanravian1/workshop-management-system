"""Supplier View Module.

Description:
- This module contains supplier view for supplier model.

"""

from ..base.view import BaseView
from .model import Supplier


class SupplierView(BaseView[Supplier]):
    """Supplier View Class.

    Description:
    - This class provides CRUD interface for Supplier model.

    """
