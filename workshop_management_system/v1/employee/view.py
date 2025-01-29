"""Employee View Module.

Description:
- This module contains employee view for employee model.

"""

from ..base.view import BaseView
from .model import Employee


class EmployeeView(BaseView[Employee]):
    """Employee View Class.

    Description:
    - This class provides CRUD interface for Employee model.

    """
