"""Payment View Module.

Description:
- This module contains Payment view for Payment model.

"""

from ..base.view import BaseView
from .model import Payment


class PaymentView(BaseView[Payment]):
    """Payment View Class.

    Description:
    - This class provides CRUD interface for Payment model.

    """
