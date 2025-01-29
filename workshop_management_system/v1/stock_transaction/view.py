"""Stock Transaction View Module.

Description:
- This module contains stock transaction view for stock transaction model.

"""

from ..base.view import BaseView
from .model import StockTransaction


class StockTransactionView(BaseView[StockTransaction]):
    """Stock Transaction View Class.

    Description:
    - This class provides CRUD interface for Stock Transaction model.

    """
