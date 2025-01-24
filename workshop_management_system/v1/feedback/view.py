"""FeedBack View Module.

Description:
- This module contains FeedBack view for FeedBack model.

"""

from ..base.view import BaseView
from .model import FeedBackTable


class CustomerView(BaseView[FeedBackTable]):
    """Customer View Class.

    Description:
    - This class provides CRUD interface for Customer model.

    """
