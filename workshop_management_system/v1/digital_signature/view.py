"""Digital Signature View Module.

Description:
- This module contains digital signature view for Digital Signature model.

"""

from ..base.view import BaseView
from .model import DigitalSignature


class DigitalSignatureView(BaseView[DigitalSignature]):
    """DigitalSignature View Class.

    Description:
    - This class provides CRUD interface for DigitalSignature model.

    """
