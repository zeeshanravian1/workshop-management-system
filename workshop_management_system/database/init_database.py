"""Insert initial data in database.

Description:
- This module is responsible for inserting initial data in database.

"""

import logging

from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError, ProgrammingError

from workshop_management_system.core.config import (
    SUPERUSER_EMAIL,
    SUPERUSER_NAME,
    SUPERUSER_PASSWORD,
    SUPERUSER_USERNAME,
)
from workshop_management_system.v1.employee.model import EmployeeTable
from workshop_management_system.v1.complaint.model import ComplaintTable
from workshop_management_system.v1.customer.model import CustomerTable
from workshop_management_system.v1.digital_signature.model import DigitalSignatureTable
from workshop_management_system.v1.estimate.model import EstimateTable
from workshop_management_system.v1.inventory.model import InventoryTable
from workshop_management_system.v1.jobcard.model import JobCardTable
from workshop_management_system.v1.notification.model import NotificationTable
from workshop_management_system.v1.payment.model import PaymentTable
from workshop_management_system.v1.service.model import ServiceTable
from workshop_management_system.v1.service_item.model import ServiceItemTable
from workshop_management_system.v1.stock_transaction.model import StockTransactionTable
from workshop_management_system.v1.supplier.model import SupplierTable
from workshop_management_system.v1.vehicle.model import VehicleTable
from .session import get_session

db_create_logger: logging.Logger = logging.getLogger(name=__name__)


def create_super_admin() -> None:
    """Create Super Admin.

    Description:
    - This function is used to create super admin in database.

    Parameter:
    - **None**

    Return:
    - **None**

    """
    try:
        with get_session() as session:
            # Create super admin
            super_user = EmployeeTable(
                name=SUPERUSER_NAME,
                username=SUPERUSER_USERNAME,
                email=SUPERUSER_EMAIL,
                password=pbkdf2_sha256.hash(SUPERUSER_PASSWORD),
            )

            session.add(super_user)
            session.commit()

    except (IntegrityError, ProgrammingError) as err:
        db_create_logger.exception(msg=err)

    except Exception as err:
        db_create_logger.exception(msg=err)
