"""JobCard View Module.

Description:
- This module contains JobCard view for JobCard model.

"""

from ..base.view import BaseView
from .model import JobCard


class JobCardView(BaseView[JobCard]):
    """JobCard View Class.

    Description:
    - This class provides CRUD interface for JobCard model.

    """
