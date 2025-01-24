"""Customer View Module.

Description:
- This module contains customer view for customer model.

"""

from ..base.view import BaseView
from .model import EstimateTable


class CustomerView(BaseView[EstimateTable]):
    """Customer View Class.

    Description:
    - This class provides CRUD interface for Customer model.

    """
