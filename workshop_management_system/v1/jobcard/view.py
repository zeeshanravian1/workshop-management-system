"""JobCard View Module.

Description:
- This module contains job card view for job card model.

"""

from sqlmodel import Session

from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory_jobcard_link.model import (
    InventoryJobCardLink,
)

from ..base.view import BaseView
from .model import JobCard


class JobCardView(BaseView[JobCard]):
    """JobCard View Class.

    Description:
    - This class provides CRUD interface for job card model.

    """

    def update_inventory(
        self,
        db_session: Session,
        record_id: int,
        previous_inventory_id: int,
        new_inventory_id: int,
    ) -> JobCard | None:
        """Update Inventory Method.

        Description:
        - This method updates inventory of job card record.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of record to update. **(Required)**
        - `previous_inventory_id` (int): Previous inventory ID. **(Required)**
        - `new_inventory_id` (int): New inventory ID. **(Required)**

        :Returns:
        - `JobCard | None`: Updated record, or None if not found.

        """
        # Check if job card record exists
        db_record: JobCard | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not db_record:
            return None

        # Check if previous inventory link exists
        inventory_link: InventoryJobCardLink | None = db_session.get(
            entity=InventoryJobCardLink,
            ident=(record_id, previous_inventory_id),
        )

        if not inventory_link:
            return None

        # Check if new inventory exists
        new_inventory: Inventory | None = db_session.get(
            entity=Inventory,
            ident=new_inventory_id,
        )

        if not new_inventory:
            return None

        # Update inventory link
        inventory_link.inventory_id = new_inventory_id
        db_session.commit()
        db_session.refresh(instance=db_record)

        return db_record
