"""Service Item View Module.

Description:
- This module contains service item view for service item model.

"""

from ..base.view import BaseView
from .model import ServiceItem


class ServiceItemView(BaseView[ServiceItem]):
    """ServiceItem View Class.

    Description:
    - This class provides CRUD interface for service item model.

    """
