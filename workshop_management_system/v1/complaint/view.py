"""Complaint View Module.

Description:
- This module contains complaint view for complaint model.

"""

from ..base.view import BaseView
from .model import Complaint


class ComplaintView(BaseView[Complaint]):
    """Complaint View Class.

    Description:
    - This class provides CRUD interface for Complaint model.

    """
