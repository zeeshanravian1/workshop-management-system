"""JobCard View Module.

Description:
- This module contains job card view for job card model.

"""

from collections.abc import Sequence

from sqlmodel import Session, select

from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView
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

    def __init__(self, model: type[JobCard]) -> None:
        """Initialize JobCardView.

        :Args:
        - `model` (type[JobCard]): JobCard model class. **(Required)**

        :Returns:
        - `None`

        """
        super().__init__(model=model)
        self.inventory_view = InventoryView(model=Inventory)

    def _validate_inventories(self, record: JobCard) -> None:
        """Validate that job card has at least one inventory item.

        :Args:
        - `record` (JobCard): JobCard record to validate. **(Required)**

        : Returns:
        - `None`

        """
        if not record.inventories:
            raise ValueError("At least one inventory item is required")

    def _get_inventory_map(
        self,
        db_session: Session,
        inventories: list[Inventory],
    ) -> dict[int, Inventory]:
        """Get and validate inventory objects from database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `inventories` (list[Inventory]): List of inventories to validate.
        **(Required)**

        :Returns:
        - `inventory_map` (dict[int, Inventory]): Map of inventory IDs to
        validated Inventory objects.

        """
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=db_session,
                record_ids=list({inv.id for inv in inventories}),
            )
        )

        return {inv.id: inv for inv in db_inventories}

    def _process_inventory_links(
        self,
        db_session: Session,
        record_id: int,
        inventories: list[Inventory],
        inventory_map: dict[int, Inventory],
        existing_links: dict[int, InventoryJobCardLink] | None = None,
    ) -> None:
        """Process inventory links for a job card.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): Job card ID. **(Required)**
        - `inventories` (list[Inventory]): List of inventories. **(Required)**
        - `inventory_map` (dict[int, Inventory]): Map of inventory IDs to
        objects. **(Required)**
        - `existing_links` (dict[int, InventoryJobCardLink] | None): Existing
        links. **(Optional)**

        :Returns:
        - `None`

        """
        if existing_links is None:
            existing_links = {}

        inventory_ids: set[int] = {inv.id for inv in inventories}

        # Process new/updated links
        for inventory in inventories:
            required_quantity: int = getattr(inventory, "_service_quantity", 1)
            db_inventory: Inventory | None = inventory_map.get(inventory.id)

            if db_inventory is None:
                raise ValueError(f"Inventory with id {inventory.id} not found")

            if inventory.quantity < inventory.minimum_threshold:
                raise ValueError(
                    f"Inventory {inventory.item_name} below minimum threshold "
                    f"({inventory.minimum_threshold}). Please restock."
                )

            if inventory.quantity < required_quantity:
                raise ValueError(
                    f"Insufficient quantity for {inventory.item_name}. "
                    f"Required: {required_quantity}, "
                    f"Available: {inventory.quantity}"
                )

            if inventory.id in existing_links:
                link: InventoryJobCardLink = existing_links[inventory.id]

                if link.quantity != required_quantity:
                    link.quantity = required_quantity

            else:
                link = InventoryJobCardLink(
                    jobcard_id=record_id,
                    inventory_id=inventory.id,
                    quantity=required_quantity,
                )
                db_session.add(instance=link)

        # Remove old links
        for inv_id in set(existing_links.keys()) - inventory_ids:
            db_session.delete(instance=existing_links[inv_id])

    def create(self, db_session: Session, record: JobCard) -> JobCard:
        """Create a new jobcard in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record` (JobCard): JobCard object to be added to database.
        **(Required)**

        :Returns:
        - `JobCard`: Created record.

        """
        self._validate_inventories(record=record)
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session, inventories=record.inventories
        )

        # Create new job card
        jobcard = JobCard(**record.model_dump())
        db_session.add(instance=jobcard)
        db_session.flush()

        # Process inventory links
        self._process_inventory_links(
            db_session=db_session,
            record_id=jobcard.id,
            inventories=record.inventories,
            inventory_map=inventory_map,
        )

        db_session.commit()
        db_session.refresh(instance=jobcard)

        return jobcard

    def create_multiple(
        self, db_session: Session, records: Sequence[JobCard]
    ) -> Sequence[JobCard]:
        """Create multiple new jobcards in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `records` (Sequence[JobCard]): JobCard objects to be added to
        database. **(Required)**

        :Returns:
        - `Sequence[JobCard]`: Created records.

        """
        # Validate all records have inventories
        all_inventories: list[Inventory] = []

        for record in records:
            self._validate_inventories(record=record)
            all_inventories.extend(record.inventories)

        # Get inventory map for all inventories
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session, inventories=all_inventories
        )

        # Create all job cards
        jobcards: list[JobCard] = []

        for record in records:
            # Create job card
            jobcard = JobCard(**record.model_dump())
            db_session.add(instance=jobcard)
            db_session.flush()

            # Process inventory links
            self._process_inventory_links(
                db_session=db_session,
                record_id=jobcard.id,
                inventories=record.inventories,
                inventory_map=inventory_map,
            )
            jobcards.append(jobcard)

        db_session.commit()

        for jobcard in jobcards:
            db_session.refresh(instance=jobcard)

        return jobcards

    def update_by_id(
        self, db_session: Session, record_id: int, record: JobCard
    ) -> JobCard | None:
        """Update a jobcard by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of job card to update. **(Required)**
        - `record` (JobCard): Jobcard model containing updated fields.
        **(Required)**

        :Returns:
        - `JobCard | None`: Updated record, or None if not found.

        """
        # Check if record exists
        db_record: JobCard | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not db_record:
            return None

        # Validate inventory presence
        self._validate_inventories(record=record)

        # Get inventory map and existing links
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session, inventories=record.inventories
        )

        # Get existing links for job card
        links: Sequence[InventoryJobCardLink] = db_session.exec(
            statement=select(InventoryJobCardLink).where(
                InventoryJobCardLink.jobcard_id == record_id
            )
        ).all()

        existing_links: dict[int, dict[int, InventoryJobCardLink]] = {
            record_id: {link.inventory_id: link for link in links}
        }

        # Update inventory links
        self._process_inventory_links(
            db_session=db_session,
            record_id=record_id,
            inventories=record.inventories,
            inventory_map=inventory_map,
            existing_links=existing_links.get(record_id, {}),
        )

        # Update job card
        db_record.sqlmodel_update(obj=record.model_dump(exclude_unset=True))
        db_session.commit()
        db_session.refresh(instance=db_record)

        return db_record

    def update_multiple_by_ids(
        self,
        db_session: Session,
        record_ids: list[int],
        records: Sequence[JobCard],
    ) -> Sequence[JobCard]:
        """Update multiple job card records by IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (list[int]): Job card IDs. **(Required)**
        - `records` (Sequence[JobCard]): Updated job card records.
        **(Required)**

        :Returns:
        - `Sequence[JobCard]`: Updated records.

        """
        if len(record_ids) != len(records):
            raise ValueError("Number of IDs must match number of records")

        updated_records: list[JobCard] = []

        for record_id, record in zip(record_ids, records, strict=True):
            updated_record: JobCard | None = self.update_by_id(
                db_session=db_session, record_id=record_id, record=record
            )

            if updated_record:
                updated_records.append(updated_record)

        return updated_records
