"""Service View Module.

Description:
- This module contains service view for service model.

"""

from sqlmodel import Session

from workshop_management_system.core.config import INVENTORY_MINIMUM_THRESHOLD
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

        Args:
            model (type[Service]): Service model class.
        """
        super().__init__(model=model)
        self.inventory_view = InventoryView(model=Inventory)

    def create(
        self,
        db_session: Session,
        record: Service,
    ) -> Service:
        """Create a new service record and manage related inventories.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record` (Service): Service object to be added to database.
        **(Required)**

        :Returns:
        - `Service`: Created record.

        """
        # Store inventory updates and quantities
        inventory_updates: list[tuple[Inventory, int]] = []

        # Verify all inventories exist and have sufficient quantity
        for inv in record.inventories:
            inventory: Inventory | None = self.inventory_view.read_by_id(
                db_session, inv.id
            )

            if not inventory:
                raise ValueError(f"Inventory with id {inv.id} not found")

            if inventory.quantity < INVENTORY_MINIMUM_THRESHOLD:
                raise ValueError(
                    f"Inventory {inventory.item_name} has reached minimum "
                    f"threshold. Please restock before creating a new service."
                )

            required_quantity: int = getattr(inv, "_service_quantity", 1)

            if inventory.quantity < required_quantity:
                raise ValueError(
                    f"Insufficient quantity for "
                    f"inventory {inventory.item_name}. "
                    f"Required: {required_quantity}, "
                    f"Available: {inventory.quantity}"
                )

            # Store inventory and quantity for later update
            inventory_updates.append((inventory, required_quantity))

        # Create service first
        service = Service(**record.model_dump())
        db_session.add(instance=service)
        db_session.flush()

        # Now create inventory links with quantities
        for inventory, quantity in inventory_updates:
            # Update inventory quantity
            inventory.quantity -= quantity

            # Create link with correct quantity
            link = InventoryServiceLink(
                service_id=service.id,
                inventory_id=inventory.id,
                quantity=quantity,
            )
            db_session.add(instance=link)

        db_session.commit()
        db_session.refresh(instance=service)

        return service
