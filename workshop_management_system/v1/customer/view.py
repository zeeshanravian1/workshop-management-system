"""Customer View Module.

Description:
- This module contains customer view for customer model.

"""

from ..base.view import BaseView
from .model import CustomerTable


class CustomerView(BaseView[CustomerTable]):
    """Customer View Class.

    Description:
    - This class provides CRUD interface for Customer model.

    """
