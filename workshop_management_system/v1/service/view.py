"""Service View Module.

Description:
- This module contains service view for service model.

"""

from ..base.view import BaseView
from .model import Service


class ServiceView(BaseView[Service]):
    """Service View Class.

    Description:
    - This class provides CRUD interface for service model.

    """
