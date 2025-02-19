"""Inventory View Module.

Description:
- This module contains inventory view for inventory model.

"""

from sqlmodel import Session

from workshop_management_system.v1.inventory_supplier_link.model import (
    InventorySupplierLink,
)
from workshop_management_system.v1.supplier.model import Supplier

from ..base.view import BaseView
from .model import Inventory


class InventoryView(BaseView[Inventory]):
    """Inventory View Class.

    Description:
    - This class provides CRUD interface for inventory model.

    """

    def update_supplier(
        self,
        db_session: Session,
        record_id: int,
        previous_supplier_id: int,
        new_supplier_id: int,
    ) -> Inventory | None:
        """Update Supplier Method.

        Description:
        - This method updates supplier of inventory record.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of record to update. **(Required)**
        - `previous_supplier_id` (int): Previous supplier ID. **(Required)**
        - `new_supplier_id` (int): New supplier ID. **(Required)**

        :Returns:
        - `Inventory | None`: Updated record, or None if not found.

        """
        # Check if inventory record exists
        db_record: Inventory | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not db_record:
            return None

        # Check if previous supplier link exists
        supplier_link: InventorySupplierLink | None = db_session.get(
            entity=InventorySupplierLink,
            ident=(record_id, previous_supplier_id),
        )

        if not supplier_link:
            return None

        # Check if new supplier exists
        new_supplier: Supplier | None = db_session.get(
            entity=Supplier,
            ident=new_supplier_id,
        )

        if not new_supplier:
            return None

        # Update supplier link
        supplier_link.supplier_id = new_supplier_id
        db_session.commit()
        db_session.refresh(instance=db_record)

        return db_record
