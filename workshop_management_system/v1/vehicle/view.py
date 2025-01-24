"""Vehicle View Module.

Description:
- This module contains the vehicle view for vehicle model.

"""

from ..base.view import BaseView
from .model import VehicleTable


class VehicleView(BaseView[VehicleTable]):
    """Vehichle View Class.

    Description:
    - This class provides CRUD interface for the Vehicle model.

    """
