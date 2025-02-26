"""Service View Module.

Description:
- This module contains service view for service model.

"""

from collections.abc import Sequence

from sqlmodel import Session, select

from workshop_management_system.core.config import ServiceStatus
from workshop_management_system.v1.base.model import Message
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.inventory_service_link.model import (
    InventoryServiceLink,
)

from ..base.view import BaseView
from .model import Service


class ServiceView(BaseView[Service]):
    """Service View Class.

    Description:
    - This class provides CRUD interface for service model.

    """

    def __init__(self, model: type[Service]) -> None:
        """Initialize ServiceView.

        :Args:
        - `model` (type[Service]): Service model class. **(Required)**

        :Returns:
        - `None`

        """
        super().__init__(model=model)
        self.inventory_view = InventoryView(model=Inventory)

    def _validate_inventories(self, record: Service) -> None:
        """Validate that service has at least one inventory item.

        :Args:
        - `record` (Service): Service record to validate inventories.
        **(Required)**

        :Returns:
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

    def _get_service_links(
        self, db_session: Session, service_id: int
    ) -> dict[int, InventoryServiceLink]:
        """Get existing inventory-service links for a service.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `service_id` (int): Service ID. **(Required)**

        :Returns:
        - `inventory_service_links` (dict[int, InventoryServiceLink]): Map of
        inventory IDs to link objects.

        """
        links: Sequence[InventoryServiceLink] = db_session.exec(
            statement=select(InventoryServiceLink).where(
                InventoryServiceLink.service_id == service_id
            )
        ).all()

        return {link.inventory_id: link for link in links}

    def _validate_inventory_quantities(
        self,
        inventories: list[Inventory],
        inventory_map: dict[int, Inventory],
    ) -> dict[int, int]:
        """Validate inventory quantities and return required quantities.

        :Args:
        - `inventories` (list[Inventory]): list of inventories. **(Required)**
        - `inventory_map` (dict[int, Inventory]): Map of inventory IDs to
        objects. **(Required)**

        :Returns:
        - `required_quantities` (dict[int, int]): Map of inventory IDs to
        required quantities.

        """
        required_quantities: dict[int, int] = {}

        for inventory in inventories:
            new_quantity: int = getattr(inventory, "_service_quantity", 1)
            db_inventory: Inventory | None = inventory_map.get(inventory.id)

            if new_quantity < 1:
                raise ValueError(
                    f"Service quantity for {inventory.item_name} "
                    f"must be at least 1"
                )

            if db_inventory is None:
                raise ValueError(f"Inventory with id {inventory.id} not found")

            # Validate minimum threshold
            if db_inventory.quantity < inventory.minimum_threshold:
                raise ValueError(
                    f"Inventory {inventory.item_name} below minimum threshold "
                    f"({inventory.minimum_threshold}). Please restock."
                )

            # Validate sufficient quantity
            if db_inventory.quantity < new_quantity:
                raise ValueError(
                    f"Insufficient quantity for {inventory.item_name}. "
                    f"Required: {new_quantity}, "
                    f"Available: {db_inventory.quantity}"
                )

            required_quantities[inventory.id] = new_quantity

        return required_quantities

    def _process_inventory_changes(
        self,
        db_session: Session,
        service_id: int,
        inventories: list[Inventory],
        inventory_map: dict[int, Inventory],
        existing_links: dict[int, InventoryServiceLink] | None = None,
    ) -> None:
        """Process all inventory changes for a service operation.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `service_id` (int): Service ID. **(Required)**
        - `inventories` (list[Inventory]): list of inventories. **(Required)**
        - `inventory_map` (dict[int, Inventory]): Map of inventory IDs to
        objects. **(Required)**
        - `existing_links` (Optional[dict[int, InventoryServiceLink]]):
        Existing links. **(Optional)**

        :Returns:
        - `None`

        """
        if existing_links is None:
            existing_links = {}

        inventory_ids: set[int] = {inv.id for inv in inventories}

        # First, restore quantities for removed inventories
        for inv_id in set(existing_links.keys()) - inventory_ids:
            inv: Inventory | None = inventory_map.get(inv_id)

            if inv:
                inv.quantity += existing_links[inv_id].quantity
                db_session.add(instance=inv)

            db_session.delete(instance=existing_links[inv_id])

        # Validate inventories and get required quantities
        required_quantities: dict[int, int] = (
            self._validate_inventory_quantities(
                inventories=inventories,
                inventory_map=inventory_map,
            )
        )

        # Process inventory links
        for inventory in inventories:
            new_quantity: int = required_quantities[inventory.id]
            db_inventory: Inventory = inventory_map[inventory.id]

            # Update or create link
            if inventory.id in existing_links:
                link: InventoryServiceLink = existing_links[inventory.id]
                old_quantity: int = link.quantity

                # Update inventory quantity if necessary
                if old_quantity != new_quantity:
                    # Restore old quantity first
                    db_inventory.quantity += old_quantity
                    # Then subtract new quantity
                    db_inventory.quantity -= new_quantity
                    # Update link quantity
                    link.quantity = new_quantity

                    db_session.add(instance=link)

            else:
                # Create new link
                link = InventoryServiceLink(
                    inventory_id=inventory.id,
                    service_id=service_id,
                    quantity=new_quantity,
                )
                db_session.add(instance=link)

                # Subtract quantity from inventory
                db_inventory.quantity -= new_quantity

            db_session.add(instance=db_inventory)

    def _restore_inventory_quantities(
        self,
        db_session: Session,
        service_id: int,
        exclude_completed: bool = False,
    ) -> None:
        """Restore inventory quantities for a service.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `service_id` (int): Service ID. **(Required)**
        - `exclude_completed` (bool): Whether to skip restoration for
        completed services. **(Optional)**

        :Returns:
        - `None`

        """
        # Check service status if needed
        if exclude_completed:
            service: Service | None = self.read_by_id(
                db_session=db_session, record_id=service_id
            )

            if service and service.status == ServiceStatus.COMPLETED:
                return

        # Get service-inventory links
        links: dict[int, InventoryServiceLink] = self._get_service_links(
            db_session=db_session, service_id=service_id
        )

        if not links:
            return

        # Get inventory objects
        inventory_ids = list(links.keys())
        inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=db_session, record_ids=inventory_ids
            )
        )
        inventory_map: dict[int, Inventory] = {
            inv.id: inv for inv in inventories
        }

        # Restore quantities for each inventory item
        for inv_id, link in links.items():
            inventory: Inventory | None = inventory_map.get(inv_id)

            if inventory:
                inventory.quantity += link.quantity
                db_session.add(instance=inventory)

        # Delete links
        for link in links.values():
            db_session.delete(instance=link)

    def create(self, db_session: Session, record: Service) -> Service:
        """Create a new service in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record` (Service): Service object to be added to database.
        **(Required)**

        :Returns:
        - `record` (Service): Created record.

        """
        self._validate_inventories(record=record)
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session, inventories=record.inventories
        )

        # Create new service
        service = Service(**record.model_dump())
        db_session.add(instance=service)
        db_session.flush()

        # Process inventory links and update quantities
        self._process_inventory_changes(
            db_session=db_session,
            service_id=service.id,
            inventories=record.inventories,
            inventory_map=inventory_map,
        )

        db_session.commit()
        db_session.refresh(instance=service)

        return service

    def create_multiple(
        self, db_session: Session, records: Sequence[Service]
    ) -> Sequence[Service]:
        """Create multiple new services in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `records` (Sequence[Service]): Service objects to be added to
        database. **(Required)**

        :Returns:
        - `records` (Sequence[Service]): Created records.

        """
        all_inventories: list[Inventory] = []

        for record in records:
            self._validate_inventories(record=record)
            all_inventories.extend(record.inventories)

        # Get inventory map for all inventories
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session, inventories=all_inventories
        )

        # Create all services
        services: list[Service] = []

        for record in records:
            service = Service(**record.model_dump())
            db_session.add(instance=service)
            db_session.flush()

            self._process_inventory_changes(
                db_session=db_session,
                service_id=service.id,
                inventories=record.inventories,
                inventory_map=inventory_map,
            )
            services.append(service)

        db_session.commit()

        for service in services:
            db_session.refresh(instance=service)

        return services

    def update_by_id(
        self, db_session: Session, record_id: int, record: Service
    ) -> Service | None:
        """Update a service by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of service to update. **(Required)**
        - `record` (Service): Service model containing updated fields.
        **(Required)**

        :Returns:
        - `record` (Service): Updated record, or None if not found.

        """
        # Check if record exists
        db_record: Service | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not db_record:
            return None

        # Validate inventory presence
        self._validate_inventories(record=record)

        # Get existing links for service
        existing_links: dict[int, InventoryServiceLink] = (
            self._get_service_links(
                db_session=db_session, service_id=record_id
            )
        )

        # Get all inventory IDs needed (existing and new)
        all_inventory_ids: set[int] = set(existing_links.keys()) | {
            inv.id for inv in record.inventories
        }

        # Get inventory map for all inventories
        inventory_map: dict[int, Inventory] = self._get_inventory_map(
            db_session=db_session,
            inventories=[
                Inventory(id=inv_id)  # type: ignore
                for inv_id in all_inventory_ids
            ],
        )

        # Process inventory links
        self._process_inventory_changes(
            db_session=db_session,
            service_id=record_id,
            inventories=record.inventories,
            inventory_map=inventory_map,
            existing_links=existing_links,
        )

        # Update service record
        db_record.sqlmodel_update(obj=record.model_dump(exclude_unset=True))
        db_session.commit()
        db_session.refresh(instance=db_record)

        return db_record

    def update_multiple_by_ids(
        self,
        db_session: Session,
        record_ids: list[int],
        records: Sequence[Service],
    ) -> Sequence[Service]:
        """Update multiple service records by IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (list[int]): Service IDs. **(Required)**
        - `records` (Sequence[Service]): Updated service records.
        **(Required)**

        :Returns:
        - `records` (Sequence[Service]): Updated records.

        """
        if len(record_ids) != len(records):
            raise ValueError("Number of IDs must match number of records")

        updated_records: list[Service] = []

        for record_id, record in zip(record_ids, records, strict=True):
            updated_record: Service | None = self.update_by_id(
                db_session=db_session,
                record_id=record_id,
                record=record,
            )

            if updated_record:
                updated_records.append(updated_record)

        return updated_records

    def delete_by_id(
        self, db_session: Session, record_id: int
    ) -> Message | None:
        """Delete a service by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of service to delete. **(Required)**

        :Returns:
        - `message` (Message): Message indicating that service has been
        deleted, or None if not found.

        """
        # Check if record exists
        record: Service | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not record:
            return None

        # Restore inventory quantities if not completed
        self._restore_inventory_quantities(
            db_session=db_session, service_id=record_id, exclude_completed=True
        )

        # Delete service
        db_session.delete(instance=record)
        db_session.commit()

        return Message(message="Record deleted successfully")

    def delete_multiple_by_ids(
        self, db_session: Session, record_ids: list[int]
    ) -> Message:
        """Delete multiple services by their IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (list[int]): list of service IDs. **(Required)**

        :Returns:
        - `message` (Message): Message indicating that services have been
        deleted.

        """
        # Get all services
        services: Sequence[Service] = self.read_multiple_by_ids(
            db_session=db_session, record_ids=record_ids
        )

        if not services:
            return Message(message="No services found to delete")

        # Process each service
        for service in services:
            # Delete by ID to handle inventory restoration
            self.delete_by_id(db_session=db_session, record_id=service.id)

        return Message(message="Records deleted successfully")
