"""Notification View Module.

Description:
- This module contains Notification view for Notification model.

"""

from ..base.view import BaseView
from .model import Notification


class NotificationView(BaseView[Notification]):
    """Notification View Class.

    Description:
    - This class provides CRUD interface for Notification model.

    """
