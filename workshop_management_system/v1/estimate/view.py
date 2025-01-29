"""Estimate View Module.

Description:
- This module contains estimate view for estimate model.

"""

from ..base.view import BaseView
from .model import Estimate


class EstimateView(BaseView[Estimate]):
    """Estimate View Class.

    Description:
    - This class provides CRUD interface for Estimate model.

    """
