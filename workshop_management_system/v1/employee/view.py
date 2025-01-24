"""Vehicle View Module.

Description:
- This module contains vehicle view for vehicle model.

"""

from ..base.view import BaseView
from .model import EmployeeTable


class VehicleView(BaseView[EmployeeTable]):
    """Vehichle View Class.

    Description:
    - This class provides CRUD interface for Vehicle model.

    """
