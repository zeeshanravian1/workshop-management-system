"""FeedBack View Module.

Description:
- This module contains FeedBack view for FeedBack model.

"""

from ..base.view import BaseView
from .model import FeedBack


class FeedBackView(BaseView[FeedBack]):
    """FeedBack View Class.

    Description:
    - This class provides CRUD interface for FeedBack model.

    """
