"""Service Test Cases.

Description:
- This file contains test cases for service operations.

"""

from collections.abc import Sequence
from datetime import date, timedelta

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import col, select

from tests.conftest import TestSetup
from workshop_management_system.core.config import (
    InventoryCategory,
    ServiceStatus,
)
from workshop_management_system.v1.base.model import Message, PaginationBase
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView
from workshop_management_system.v1.inventory.model import (
    Inventory,
    InventoryBase,
)
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.inventory_service_link.model import (
    InventoryServiceLink,
)
from workshop_management_system.v1.service.model import Service, ServiceBase
from workshop_management_system.v1.service.view import ServiceView
from workshop_management_system.v1.supplier.model import Supplier, SupplierBase
from workshop_management_system.v1.supplier.view import SupplierView
from workshop_management_system.v1.vehicle.model import Vehicle, VehicleBase
from workshop_management_system.v1.vehicle.view import VehicleView


# pylint: disable=protected-access
class TestService(TestSetup):
    """Test cases for service operations.

    Description:
    - This class provides test cases for service operations.

    """

    customer_view: CustomerView
    test_customer: Customer
    vehicle_view: VehicleView
    test_vehicle_1: Vehicle
    test_vehicle_2: Vehicle

    supplier_view: SupplierView
    test_supplier: Supplier
    inventory_view: InventoryView
    test_inventory_1: Inventory
    test_inventory_2: Inventory
    test_inventory_3: Inventory

    service_view: ServiceView
    test_service_1: ServiceBase
    test_service_2: ServiceBase
    test_service_3: ServiceBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.customer_view = CustomerView(Customer)
        self.vehicle_view = VehicleView(Vehicle)
        self.supplier_view = SupplierView(Supplier)
        self.inventory_view = InventoryView(Inventory)
        self.service_view = ServiceView(Service)

        # Create customer instances for validation
        customer: CustomerBase = CustomerBase(
            name="Test Customer",
            email="test@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address",
        )

        self.test_customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**customer.model_dump()),
        )

        # Create vehicle instances for validation
        vehicle_1: VehicleBase = VehicleBase(
            make="Toyota",
            model="Corolla",
            year=2020,
            vehicle_number="ABC-1234",
            customer_id=self.test_customer.id,
        )
        vehicle_2: VehicleBase = VehicleBase(
            make="Honda",
            model="Civic",
            year=2021,
            vehicle_number="DEF-4567",
            customer_id=self.test_customer.id,
        )

        self.test_vehicle_1 = self.vehicle_view.create(
            db_session=self.session, record=Vehicle(**vehicle_1.model_dump())
        )
        self.test_vehicle_2 = self.vehicle_view.create(
            db_session=self.session, record=Vehicle(**vehicle_2.model_dump())
        )

        # Create supplier instances for validation
        supplier: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address",
        )

        self.test_supplier = self.supplier_view.create(
            db_session=self.session, record=Supplier(**supplier.model_dump())
        )

        # Create inventory instances for validation
        inventory_1: InventoryBase = InventoryBase(
            item_name="Test Item 1",
            quantity=50,
            unit_price=100,
            minimum_threshold=5,
            category=InventoryCategory.ELECTRICALS,
        )
        inventory_2: InventoryBase = InventoryBase(
            item_name="Test Item 2",
            quantity=100,
            unit_price=200,
            minimum_threshold=10,
            category=InventoryCategory.SPARE_PARTS,
        )
        inventory_3: InventoryBase = InventoryBase(
            item_name="Test Item 3",
            quantity=30,
            unit_price=300,
            minimum_threshold=15,
            category=InventoryCategory.TOOLS,
        )

        self.test_inventory_1 = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **inventory_1.model_dump(), suppliers=[self.test_supplier]
            ),
        )
        self.test_inventory_2 = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **inventory_2.model_dump(), suppliers=[self.test_supplier]
            ),
        )
        self.test_inventory_3 = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **inventory_3.model_dump(), suppliers=[self.test_supplier]
            ),
        )

        # Create service instances for validation
        self.test_service_1 = ServiceBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Service 1",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_service_2 = ServiceBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Service 2",
            vehicle_id=self.test_vehicle_2.id,
        )
        self.test_service_3 = ServiceBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Service 3",
            vehicle_id=self.test_vehicle_1.id,
        )

    def test_status_validation(self) -> None:
        """Validating status."""
        with pytest.raises(expected_exception=ValidationError) as exc_info:
            ServiceBase(
                status="Invalid Status",  # type: ignore
                service_date=date.today(),
                description="Test Service",
                vehicle_id=self.test_vehicle_1.id,
            )

        statuses: list[str] = [f"'{key.value}'" for key in ServiceStatus]
        validation: str = (
            " or ".join([", ".join(statuses[:-1]), statuses[-1]])
            if len(statuses) > 1
            else statuses[0]
        )

        assert f"Input should be {validation}" in str(exc_info.value)

    def test_validate_service_date(self) -> None:
        """Validating service date."""
        # Check for invalid date
        with pytest.raises(expected_exception=ValidationError) as exc_info:
            ServiceBase(
                status=ServiceStatus.PENDING,
                service_date="Invalid Date",  # type: ignore
                description="Test Service",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Input should be a valid date or datetime" in str(
            exc_info.value
        )

        # Check if date is in past
        with pytest.raises(expected_exception=ValidationError) as exc_info:
            ServiceBase(
                status=ServiceStatus.PENDING,
                service_date=date.today() - timedelta(days=1),
                description="Test Service",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Date cannot be in past." in str(exc_info.value)

    def test_create_service_single_inventory(self) -> None:
        """Creating a service single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        result: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_service_1.model_dump()
        )
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

        # Verify inventory quantity in inventory-service links
        inventory_service_link: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_link is not None
        assert (
            inventory_service_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert (
            db_inventory.quantity
            == initial_quantity - self.test_inventory_1._service_quantity
        )

    def test_create_service_multiple_inventories(self) -> None:
        """Creating a service multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create service
        result: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_service_2.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_service_links, key=lambda x: x.inventory_id),
                sorted(
                    [self.test_inventory_1, self.test_inventory_2],
                    key=lambda x: x.id,
                ),
                strict=True,
            )
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[i.id for i in result.inventories],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - db_inventory._service_quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_create_service_required_quantity_exceeds_available_quantity(
        self,
    ) -> None:
        """Creating a service required quantity exceeds available quantity."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 100

        # Create service
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.create(
                db_session=self.session,
                record=Service(
                    **self.test_service_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_1.item_name}. "
            f"Required: {self.test_inventory_1._service_quantity}, "
            f"Available: {self.test_inventory_1.quantity}"
            in str(exc_info.value)
        )

    def test_create_service_inventory_quantity_exceeds_inventory_threshold(
        self,
    ) -> None:
        """Creating service inventory quantity exceeds inventory threshold."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 1000

        # Create service
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.create(
                db_session=self.session,
                record=Service(
                    **self.test_service_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_1.item_name}. "
            f"Required: {self.test_inventory_1._service_quantity}, "
            f"Available: {self.test_inventory_1.quantity}"
            in str(exc_info.value)
        )

    def test_create_service_no_inventory(self) -> None:
        """Creating a service without inventory."""
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.create(
                db_session=self.session,
                record=Service(**self.test_service_1.model_dump()),
            )

        assert "At least one inventory item is required" in str(exc_info.value)

    def test_create_multiple_services(self) -> None:
        """Test creating multiple services inventory relationships."""
        # Set different inventory quantities for each service
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create test data with different inventory combinations
        service_1 = Service(
            **self.test_service_1.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )
        service_2 = Service(
            **self.test_service_2.model_dump(),
            inventories=[self.test_inventory_2],
        )

        # Create services
        result: Sequence[Service] = self.service_view.create_multiple(
            db_session=self.session, records=[service_1, service_2]
        )

        assert len(result) == 2
        assert all(service.id is not None for service in result)
        assert all(service.created_at is not None for service in result)
        assert all(service.updated_at is None for service in result)
        assert all(
            service.model_dump(exclude={"id", "created_at", "updated_at"})
            in [
                self.test_service_1.model_dump(),
                self.test_service_2.model_dump(),
            ]
            for service in result
        )
        assert all(len(service.inventories) > 0 for service in result)

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter(
                    col(column_expression=InventoryServiceLink.service_id).in_(
                        [service.id for service in result]
                    )
                )
            )
        ).all()

        service_inventory_quantity: dict[tuple[int, int], int] = {
            (link.service_id, link.inventory_id): link.quantity
            for link in inventory_service_links
        }

        assert inventory_service_links is not None
        assert len(inventory_service_links) == 3
        assert all(
            service_inventory_quantity[(service.id, inventory.id)]
            == inventory._service_quantity
            for service in result
            for inventory in service.inventories
        )

        # Verify inventories quantity persists in inventory
        inventory_usage: dict[int, int] = {
            item: sum(
                val
                for (_, i), val in service_inventory_quantity.items()
                if i == item
            )
            for item in {k[1] for k in service_inventory_quantity}
        }

        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=list(inventory_usage.keys()),
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity
            == quantity - inventory_usage[db_inventory.id]
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_create_multiple_services_different_quantities(self) -> None:
        """Test creating multiple services different inventory quantities."""
        # Set different inventory quantities for each service
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        quantities: dict[str, dict[int, int]] = {
            "service_1": {
                self.test_inventory_1.id: (
                    self.test_inventory_1._service_quantity
                ),
                self.test_inventory_2.id: (
                    self.test_inventory_2._service_quantity
                ),
            },
        }

        # Create test data with different inventory combinations
        service_1 = Service(
            **self.test_service_1.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )

        db_service_1: Service = self.service_view.create(
            db_session=self.session, record=service_1
        )

        # Set different inventory quantities for each service
        self.test_inventory_1._service_quantity = 5
        self.test_inventory_2._service_quantity = 15

        quantities["service_2"] = {
            self.test_inventory_1.id: self.test_inventory_1._service_quantity,
            self.test_inventory_2.id: self.test_inventory_2._service_quantity,
        }

        service_2 = Service(
            **self.test_service_2.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )

        db_service_2: Service = self.service_view.create(
            db_session=self.session, record=service_2
        )

        assert db_service_1.id is not None
        assert db_service_2.id is not None
        assert db_service_1.created_at is not None
        assert db_service_2.created_at is not None
        assert db_service_1.updated_at is None
        assert db_service_2.updated_at is None
        assert (
            db_service_1.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_service_1.model_dump()
        )
        assert (
            db_service_2.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_service_2.model_dump()
        )
        assert len(db_service_1.inventories) == 2
        assert len(db_service_2.inventories) == 2

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter(
                    col(column_expression=InventoryServiceLink.service_id).in_(
                        [db_service_1.id, db_service_2.id]
                    )
                )
            )
        ).all()

        service_inventory_quantity: dict[tuple[int, int], int] = {
            (link.service_id, link.inventory_id): link.quantity
            for link in inventory_service_links
        }

        assert inventory_service_links is not None
        assert len(inventory_service_links) == 4
        assert all(
            service_inventory_quantity[(service.id, inventory.id)]
            == quantities[f"service_{idx + 1}"][inventory.id]
            for idx, service in enumerate([db_service_1, db_service_2])
            for inventory in service.inventories
        )

        # Verify inventories quantity persists in inventory
        inventory_usage: dict[int, int] = {
            item: sum(
                val
                for (_, i), val in service_inventory_quantity.items()
                if i == item
            )
            for item in {k[1] for k in service_inventory_quantity}
        }

        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=list(inventory_usage.keys()),
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity
            == quantity - inventory_usage[db_inventory.id]
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_service_by_id_single_inventory(self) -> None:
        """Retrieving a service by ID single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Read service by ID
        result: Service | None = self.service_view.read_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert result is not None
        assert result.model_dump() == db_service.model_dump()
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_link: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_link is not None
        assert (
            inventory_service_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert (
            db_inventory.quantity
            == initial_quantity - self.test_inventory_1._service_quantity
        )

    def test_read_service_by_id_multiple_inventories(self) -> None:
        """Retrieving a service by ID multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Read service by ID
        result: Service | None = self.service_view.read_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert result is not None
        assert result.model_dump() == db_service.model_dump()
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_service_links, key=lambda x: x.inventory_id),
                sorted(
                    [self.test_inventory_1, self.test_inventory_2],
                    key=lambda x: x.id,
                ),
                strict=True,
            )
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[i.id for i in result.inventories],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - db_inventory._service_quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_non_existent_service(self) -> None:
        """Retrieving a non-existent service."""
        non_existent_id: int = -1

        result: Service | None = self.service_view.read_by_id(
            db_session=self.session,
            record_id=non_existent_id,
        )

        assert result is None

    def test_read_multiple_services_by_ids(self) -> None:
        """Retrieving multiple services by IDs."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple services
        result: Sequence[Service] = self.service_view.create_multiple(
            db_session=self.session,
            records=[
                Service(
                    **self.test_service_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                Service(
                    **self.test_service_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        retrieved_services: Sequence[Service] = (
            self.service_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[j.id for j in result],
            )
        )

        assert len(retrieved_services) == len(result)
        assert all(
            rj.model_dump() == j.model_dump()
            for rj, j in zip(retrieved_services, result, strict=False)
        )
        assert all(
            inventory in service.inventories
            for service, inventory in zip(
                retrieved_services,
                [self.test_inventory_1, self.test_inventory_2],
                strict=False,
            )
        )

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter(
                    col(column_expression=InventoryServiceLink.service_id).in_(
                        [service.id for service in retrieved_services]
                    )
                )
            )
        ).all()

        service_inventory_quantity: dict[tuple[int, int], int] = {
            (link.service_id, link.inventory_id): link.quantity
            for link in inventory_service_links
        }

        assert inventory_service_links is not None
        assert len(inventory_service_links) == 2
        assert all(
            service_inventory_quantity[(service.id, inventory.id)]
            == inventory._service_quantity
            for service in retrieved_services
            for inventory in service.inventories
        )

        # Verify inventories quantity persists in inventory
        inventory_usage: dict[int, int] = {
            item: sum(
                val
                for (_, i), val in service_inventory_quantity.items()
                if i == item
            )
            for item in {k[1] for k in service_inventory_quantity}
        }

        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=list(inventory_usage.keys()),
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity
            == quantity - inventory_usage[db_inventory.id]
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_all_services(self) -> None:
        """Retrieving all services."""
        # Create multiple services
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )

        result: PaginationBase[Service] = self.service_view.read_all(
            db_session=self.session
        )

        assert result.current_page == 1
        assert result.limit == 10
        assert result.total_pages == 1
        assert result.total_records == 2
        assert result.next_record_id is None
        assert result.previous_record_id is None

        # Assert records content
        assert len(result.records) == 2
        assert all(
            j.description
            in [
                self.test_service_1.description,
                self.test_service_2.description,
            ]
            for j in result.records
        )

    def test_read_all_services_pagination(self) -> None:
        """Service pagination multiple pages."""
        # Create services to test pagination
        service_1: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        service_2: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        service_3: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[Service] = self.service_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == service_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert all(
            j.description in [service_1.description, service_2.description]
            and j.description != service_3.description
            for j in page1_result.records
        )

        # Test second page
        page2_result: PaginationBase[Service] = self.service_view.read_all(
            db_session=self.session, page=2, limit=2
        )

        assert page2_result.current_page == 2
        assert page2_result.limit == 2
        assert page2_result.total_pages == 2
        assert page2_result.total_records == 3
        assert page2_result.next_record_id is None
        assert page2_result.previous_record_id == 1
        assert len(page2_result.records) == 1
        assert all(
            j.description in [service_3.description]
            and j.description
            not in [service_1.description, service_2.description]
            for j in page2_result.records
        )

    def test_search_service_by_description(self) -> None:
        """Searching services by description."""
        # Create test services
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Search for services with specific description
        result: PaginationBase[Service] = self.service_view.read_all(
            db_session=self.session,
            search_by="description",
            search_query="service 1",
        )

        assert result.current_page == 1
        assert result.limit == 10
        assert result.total_pages == 1
        assert result.total_records == 1
        assert result.next_record_id is None
        assert result.previous_record_id is None

        # Assert records content
        assert len(result.records) == 1
        assert all(
            j.description == self.test_service_1.description
            for j in result.records
        )

    def test_search_service_by_invalid_column(self) -> None:
        """Search service by invalid column name."""
        # Create test services
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.read_all(
                db_session=self.session,
                search_by="invalid",
                search_query="service 1",
            )

        assert "Invalid search column" in str(exc_info.value)

    def test_update_service(self) -> None:
        """Updating a service."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )

        # Update service
        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=db_service.id,
            record=Service(
                **updated_service.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_service.model_dump()
        )
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

        # Verify inventory quantity in inventory-service links
        inventory_service_link: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_link is not None
        assert (
            inventory_service_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert (
            db_inventory.quantity
            == initial_quantity - self.test_inventory_1._service_quantity
        )

    def test_update_service_inventory_single_inventory(self) -> None:
        """Updating a service single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = 20

        # Update service
        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=db_service.id,
            record=Service(
                **updated_service.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_service.model_dump()
        )
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_link: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_link is not None
        assert (
            inventory_service_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert (
            db_inventory.quantity
            == initial_quantity - self.test_inventory_1._service_quantity
        )

    def test_update_service_add_inventory(self) -> None:
        """Updating a service by adding inventory item."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_2._service_quantity = 20

        # Update service
        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=db_service.id,
            record=Service(
                **updated_service.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_service.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_service_links, key=lambda x: x.inventory_id),
                sorted(
                    [self.test_inventory_1, self.test_inventory_2],
                    key=lambda x: x.id,
                ),
                strict=True,
            )
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[i.id for i in result.inventories],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - db_inventory._service_quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_update_service_remove_inventory(self) -> None:
        """Updating a service by removing inventory item."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(initial_db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - service_quantity
            for db_inventory, quantity, service_quantity in zip(
                sorted(initial_db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                [
                    self.test_inventory_1._service_quantity,
                    self.test_inventory_2._service_quantity,
                ],
                strict=True,
            )
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )

        # Update service
        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=db_service.id,
            record=Service(
                **updated_service.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_service.model_dump()
        )
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 not in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_links is not None
        assert len(inventory_service_links) == 1
        assert (
            inventory_service_links[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify final inventory quantities after update
        updated_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(updated_db_inventories) == 2
        assert all(
            db_inventory.quantity
            == (
                quantity - service_quantity
                if db_inventory.id == self.test_inventory_1.id
                else quantity
            )
            for db_inventory, quantity, service_quantity in zip(
                sorted(updated_db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                [self.test_inventory_1._service_quantity, 0],
                strict=True,
            )
        )

    def test_update_service_multiple_inventories(self) -> None:
        """Updating a service multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(initial_db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - service_quantity
            for db_inventory, quantity, service_quantity in zip(
                sorted(initial_db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                [
                    self.test_inventory_1._service_quantity,
                    self.test_inventory_2._service_quantity,
                ],
                strict=True,
            )
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = 5
        self.test_inventory_2._service_quantity = 15

        # Update service
        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=db_service.id,
            record=Service(
                **updated_service.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_service.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=result.id
                )
            )
        ).all()

        assert inventory_service_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_service_links, key=lambda x: x.inventory_id),
                sorted(
                    [self.test_inventory_1, self.test_inventory_2],
                    key=lambda x: x.id,
                ),
                strict=True,
            )
        )

        # Verify final inventory quantities after update
        updated_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(updated_db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity - service_quantity
            for db_inventory, quantity, service_quantity in zip(
                sorted(updated_db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                [
                    self.test_inventory_1._service_quantity,
                    self.test_inventory_2._service_quantity,
                ],
                strict=True,
            )
        )

    def test_update_service_non_existent_inventory(self) -> None:
        """Updating a service with non-existent inventory item."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )

        inventory_id: int = -1

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.update_by_id(
                db_session=self.session,
                record_id=db_service.id,
                record=Service(
                    **updated_service.model_dump(),
                    inventories=[Inventory(id=inventory_id)],  # type: ignore
                ),
            )

        assert f"Inventory with id {inventory_id} not found" in str(
            exc_info.value
        )

    def test_update_service_inventory_quantity_negative(self) -> None:
        """Updating a service with negative inventory quantity."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = -1

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.update_by_id(
                db_session=self.session,
                record_id=db_service.id,
                record=Service(
                    **updated_service.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Service quantity for {self.test_inventory_1.item_name} "
            "must be at least 1" in str(exc_info.value)
        )

    def test_update_service_inventory_quantity_exceeds_available_quantity(
        self,
    ) -> None:
        """Updating a service required quantity exceeds available quantity."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = initial_quantity + 1

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.update_by_id(
                db_session=self.session,
                record_id=db_service.id,
                record=Service(
                    **updated_service.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_1.item_name}. "
            f"Required: {self.test_inventory_1._service_quantity}, "
            f"Available: {self.test_inventory_1.quantity}"
            in str(exc_info.value)
        )

    def test_update_service_inventory_quantity_exceeds_inventory_threshold(
        self,
    ) -> None:
        """Updating a service required quantity exceeds inventory threshold."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_2.id,
        )
        self.test_inventory_2._service_quantity = 1000

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.update_by_id(
                db_session=self.session,
                record_id=db_service.id,
                record=Service(
                    **updated_service.model_dump(),
                    inventories=[self.test_inventory_1, self.test_inventory_2],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_2.item_name}. "
            f"Required: {self.test_inventory_2._service_quantity}, "
            f"Available: {self.test_inventory_2.quantity}"
            in str(exc_info.value)
        )

    def test_update_non_existent_service(self) -> None:
        """Updating a non-existent service."""
        non_existent_id: int = -1

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )

        result: Service | None = self.service_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=Service(**updated_service.model_dump()),
        )

        assert result is None

    def test_update_service_no_inventory(self) -> None:
        """Updating a service without inventory."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_service: ServiceBase = ServiceBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test service",
            vehicle_id=self.test_vehicle_1.id,
        )

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.service_view.update_by_id(
                db_session=self.session,
                record_id=db_service.id,
                record=Service(**updated_service.model_dump()),
            )

        assert "At least one inventory item is required" in str(exc_info.value)

    def test_update_multiple_services(self) -> None:
        """Updating multiple services."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple services
        result: Sequence[Service] = self.service_view.create_multiple(
            db_session=self.session,
            records=[
                Service(
                    **self.test_service_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                Service(
                    **self.test_service_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        # Map inventories by ID for easier assertions
        initial_inventory_map: dict[int, Inventory] = {
            inv.id: inv for inv in initial_db_inventories
        }

        assert len(initial_db_inventories) == 2
        assert all(service.id is not None for service in result)
        assert all(service.created_at is not None for service in result)
        assert all(service.updated_at is None for service in result)

        # Verify initial quantities
        assert all(
            initial_inventory_map[inv_id].quantity
            == initial_quantity - service_quantity
            for inv_id, initial_quantity, service_quantity in zip(
                [self.test_inventory_1.id, self.test_inventory_2.id],
                [initial_quantity_1, initial_quantity_2],
                [
                    self.test_inventory_1._service_quantity,
                    self.test_inventory_2._service_quantity,
                ],
                strict=True,
            )
        )

        # Verify inventory quantity in inventory-service links
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter(
                    col(column_expression=InventoryServiceLink.service_id).in_(
                        [service.id for service in result]
                    )
                )
            ).all()
        )

        initial_service_inventory_quantity: dict[tuple[int, int], int] = {
            (link.service_id, link.inventory_id): link.quantity
            for link in inventory_service_links
        }

        assert inventory_service_links is not None
        assert len(inventory_service_links) == 2
        assert all(
            initial_service_inventory_quantity[(service.id, inventory.id)]
            == inventory._service_quantity
            for service in result
            for inventory in service.inventories
        )

        updated_services: Sequence[ServiceBase] = [
            ServiceBase(
                status=ServiceStatus.IN_PROGRESS,
                service_date=date.today() + timedelta(days=1),
                description="Updated Test service",
                vehicle_id=self.test_vehicle_1.id,
            )
            for _ in result
        ]
        self.test_inventory_1._service_quantity = 5

        # Update multiple services
        updated_result: Sequence[Service] = (
            self.service_view.update_multiple_by_ids(
                db_session=self.session,
                records=[
                    Service(
                        **updated_service.model_dump(),
                        inventories=[self.test_inventory_1],
                    )
                    for updated_service in updated_services
                ],
                record_ids=[j.id for j in result],
            )
        )

        assert len(updated_result) == len(result)
        assert all(j.created_at is not None for j in updated_result)
        assert all(j.updated_at is not None for j in updated_result)
        assert all(
            j.model_dump(exclude={"id", "created_at", "updated_at"})
            == u.model_dump()
            for j, u in zip(updated_result, updated_services, strict=False)
        )
        assert all(len(j.inventories) == 1 for j in updated_result)
        assert all(
            self.test_inventory_1 in j.inventories for j in updated_result
        )

        # Verify inventory quantity in inventory-service links
        updated_inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter(
                    col(column_expression=InventoryServiceLink.service_id).in_(
                        [service.id for service in updated_result]
                    )
                )
            ).all()
        )

        updated_service_inventory_quantity: dict[tuple[int, int], int] = {
            (link.service_id, link.inventory_id): link.quantity
            for link in updated_inventory_service_links
        }

        assert updated_inventory_service_links is not None
        assert len(updated_inventory_service_links) == 2

        # Each service should now use inventory_1 with quantity 5
        for service in updated_result:
            assert (
                updated_service_inventory_quantity[
                    (service.id, self.test_inventory_1.id)
                ]
                == self.test_inventory_1._service_quantity
            )

        # Verify final inventory quantities after update
        updated_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        # Map inventories by ID for easier assertions
        updated_inventory_map: dict[int, Inventory] = {
            inv.id: inv for inv in updated_db_inventories
        }

        assert len(updated_db_inventories) == 2
        assert updated_inventory_map[
            self.test_inventory_1.id
        ].quantity == initial_quantity_1 - (
            2 * self.test_inventory_1._service_quantity
        )
        assert (
            updated_inventory_map[self.test_inventory_2.id].quantity
            == initial_quantity_2
        )

    def test_delete_service(self) -> None:
        """Deleting a service."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[self.test_inventory_1.id],
            )
        )

        assert len(initial_db_inventories) == 1
        assert initial_db_inventories[0].quantity == initial_quantity - 10

        # Delete service
        result: Message | None = self.service_view.delete_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert result is not None
        assert result == Message(message="Record deleted successfully")

        # Verify service no longer exists
        retrieved_service: Service | None = self.service_view.read_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert retrieved_service is None

        # Verify inventory no longer linked to service
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=db_service.id
                )
            )
        ).all()

        assert inventory_service_links == []

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert db_inventory.quantity == initial_quantity

    def test_delete_completed_service(self) -> None:
        """Deleting a completed service."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_service_1.status = ServiceStatus.COMPLETED

        # Create service
        db_service: Service = self.service_view.create(
            db_session=self.session,
            record=Service(
                **self.test_service_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[self.test_inventory_1.id],
            )
        )

        assert len(initial_db_inventories) == 1
        assert initial_db_inventories[0].quantity == initial_quantity - 10

        # Delete service
        result: Message | None = self.service_view.delete_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert result is not None
        assert result == Message(message="Record deleted successfully")

        # Verify service no longer exists
        retrieved_service: Service | None = self.service_view.read_by_id(
            db_session=self.session, record_id=db_service.id
        )

        assert retrieved_service is None

        # Verify inventory no longer linked to service
        inventory_service_links: Sequence[InventoryServiceLink] = (
            self.session.exec(
                statement=select(InventoryServiceLink).filter_by(
                    service_id=db_service.id
                )
            )
        ).all()

        assert inventory_service_links == []

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert (
            db_inventory.quantity
            == initial_quantity - self.test_inventory_1._service_quantity
        )

    def test_delete_non_existent_service(self) -> None:
        """Deleting a non-existent service."""
        non_existent_id: int = -1

        result: Message | None = self.service_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_delete_multiple_services_by_ids(self) -> None:
        """Deleting multiple services by IDs."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple services
        self.service_view.create_multiple(
            db_session=self.session,
            records=[
                Service(
                    **self.test_service_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                Service(
                    **self.test_service_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        # Verify initial inventory quantities after creation
        initial_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        sorted_inventories: list[Inventory] = sorted(
            initial_db_inventories, key=lambda x: x.id
        )
        assert len(sorted_inventories) == 2
        assert sorted_inventories[0].quantity == initial_quantity_1 - 10
        assert sorted_inventories[1].quantity == initial_quantity_2 - 20

        # Delete multiple services
        result: Message | None = self.service_view.delete_multiple_by_ids(
            db_session=self.session,
            record_ids=[service.id for service in sorted_inventories],
        )

        assert result is not None
        assert result == Message(message="Records deleted successfully")

        # Verify services no longer exist
        retrieved_services: Sequence[Service] = (
            self.service_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[service.id for service in sorted_inventories],
            )
        )

        assert retrieved_services == []

        # Verify inventory quantity persists in inventory
        updated_db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(updated_db_inventories) == 2
        assert updated_db_inventories[0].quantity == initial_quantity_1
        assert updated_db_inventories[1].quantity == initial_quantity_2
