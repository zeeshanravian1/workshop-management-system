"""JobCard Test Cases.

Description:
- This file contains test cases for job card operations.

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
from workshop_management_system.v1.inventory_jobcard_link.model import (
    InventoryJobCardLink,
)
from workshop_management_system.v1.jobcard.model import JobCard, JobCardBase
from workshop_management_system.v1.jobcard.view import JobCardView
from workshop_management_system.v1.supplier.model import Supplier, SupplierBase
from workshop_management_system.v1.supplier.view import SupplierView
from workshop_management_system.v1.vehicle.model import Vehicle, VehicleBase
from workshop_management_system.v1.vehicle.view import VehicleView


# pylint: disable=protected-access
class TestJobCard(TestSetup):
    """Test cases for job card operations.

    Description:
    - This class provides test cases for job card operations.

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

    jobcard_view: JobCardView
    test_jobcard_1: JobCardBase
    test_jobcard_2: JobCardBase
    test_jobcard_3: JobCardBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.customer_view = CustomerView(Customer)
        self.vehicle_view = VehicleView(Vehicle)
        self.supplier_view = SupplierView(Supplier)
        self.inventory_view = InventoryView(Inventory)
        self.jobcard_view = JobCardView(JobCard)

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

        # Create job card instances for validation
        self.test_jobcard_1 = JobCardBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Job Card 1",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_jobcard_2 = JobCardBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Job Card 2",
            vehicle_id=self.test_vehicle_2.id,
        )
        self.test_jobcard_3 = JobCardBase(
            status=ServiceStatus.PENDING,
            service_date=date.today(),
            description="Test Job Card 3",
            vehicle_id=self.test_vehicle_1.id,
        )

    def test_status_validation(self) -> None:
        """Validating status."""
        with pytest.raises(expected_exception=ValidationError) as exc_info:
            JobCardBase(
                status="Invalid Status",  # type: ignore
                service_date=date.today(),
                description="Test Job Card",
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
            JobCardBase(
                status=ServiceStatus.PENDING,
                service_date="Invalid Date",  # type: ignore
                description="Test Job Card",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Input should be a valid date or datetime" in str(
            exc_info.value
        )

        # Check if date is in past
        with pytest.raises(expected_exception=ValidationError) as exc_info:
            JobCardBase(
                status=ServiceStatus.PENDING,
                service_date=date.today() - timedelta(days=1),
                description="Test Job Card",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Date cannot be in past." in str(exc_info.value)

    def test_create_jobcard_single_inventory(self) -> None:
        """Creating a job card single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        result: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_jobcard_1.model_dump()
        )
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_link: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_link is not None
        assert (
            inventory_jobcard_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert db_inventory.quantity == initial_quantity

    def test_create_jobcard_multiple_inventories(self) -> None:
        """Creating a job card multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        result: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_jobcard_2.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_jobcard_links, key=lambda x: x.inventory_id),
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
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_create_jobcard_required_quantity_exceeds_available_quantity(
        self,
    ) -> None:
        """Creating a job card required quantity exceeds available quantity."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 100

        # Create job card
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.create(
                db_session=self.session,
                record=JobCard(
                    **self.test_jobcard_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_1.item_name}. "
            f"Required: {self.test_inventory_1._service_quantity}, "
            f"Available: {self.test_inventory_1.quantity}"
            in str(exc_info.value)
        )

    def test_create_jobcard_inventory_quantity_exceeds_inventory_threshold(
        self,
    ) -> None:
        """Creating job card inventory quantity exceeds inventory threshold."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 1000

        # Create job card
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.create(
                db_session=self.session,
                record=JobCard(
                    **self.test_jobcard_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_1.item_name}. "
            f"Required: {self.test_inventory_1._service_quantity}, "
            f"Available: {self.test_inventory_1.quantity}"
            in str(exc_info.value)
        )

    def test_create_jobcard_no_inventory(self) -> None:
        """Creating a job card without inventory."""
        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.create(
                db_session=self.session,
                record=JobCard(**self.test_jobcard_1.model_dump()),
            )

        assert "At least one inventory item is required" in str(exc_info.value)

    def test_create_multiple_jobcards(self) -> None:
        """Test creating multiple job cards inventory relationships."""
        # Set different inventory quantities for each job card
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create test data with different inventory combinations
        jobcard_1 = JobCard(
            **self.test_jobcard_1.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )
        jobcard_2 = JobCard(
            **self.test_jobcard_2.model_dump(),
            inventories=[self.test_inventory_2],
        )

        # Create job cards
        result: Sequence[JobCard] = self.jobcard_view.create_multiple(
            db_session=self.session, records=[jobcard_1, jobcard_2]
        )

        assert len(result) == 2
        assert all(jobcard.id is not None for jobcard in result)
        assert all(jobcard.created_at is not None for jobcard in result)
        assert all(jobcard.updated_at is None for jobcard in result)
        assert all(
            jobcard.model_dump(exclude={"id", "created_at", "updated_at"})
            in [
                self.test_jobcard_1.model_dump(),
                self.test_jobcard_2.model_dump(),
            ]
            for jobcard in result
        )
        assert all(len(jobcard.inventories) > 0 for jobcard in result)

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter(
                    col(column_expression=InventoryJobCardLink.jobcard_id).in_(
                        [jobcard.id for jobcard in result]
                    )
                )
            )
        ).all()

        jobcard_inventory_quantity: dict[tuple[int, int], int] = {
            (link.jobcard_id, link.inventory_id): link.quantity
            for link in inventory_jobcard_links
        }

        assert inventory_jobcard_links is not None
        assert len(inventory_jobcard_links) == 3
        assert all(
            jobcard_inventory_quantity[(jobcard.id, inventory.id)]
            == inventory._service_quantity
            for jobcard in result
            for inventory in jobcard.inventories
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    inventory.id
                    for jobcard in result
                    for inventory in jobcard.inventories
                ],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_create_multiple_jobcards_different_quantities(self) -> None:
        """Test creating multiple job cards different inventory quantities."""
        # Set different inventory quantities for each job card
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        quantities: dict[str, dict[int, int]] = {
            "jobcard_1": {
                self.test_inventory_1.id: (
                    self.test_inventory_1._service_quantity
                ),
                self.test_inventory_2.id: (
                    self.test_inventory_2._service_quantity
                ),
            },
        }

        # Create test data with different inventory combinations
        jobcard_1 = JobCard(
            **self.test_jobcard_1.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )

        db_jobcard_1: JobCard = self.jobcard_view.create(
            db_session=self.session, record=jobcard_1
        )

        # Set different inventory quantities for each job card
        self.test_inventory_1._service_quantity = 5
        self.test_inventory_2._service_quantity = 15

        quantities["jobcard_2"] = {
            self.test_inventory_1.id: self.test_inventory_1._service_quantity,
            self.test_inventory_2.id: self.test_inventory_2._service_quantity,
        }

        jobcard_2 = JobCard(
            **self.test_jobcard_2.model_dump(),
            inventories=[self.test_inventory_1, self.test_inventory_2],
        )

        db_jobcard_2: JobCard = self.jobcard_view.create(
            db_session=self.session, record=jobcard_2
        )

        assert db_jobcard_1.id is not None
        assert db_jobcard_2.id is not None
        assert db_jobcard_1.created_at is not None
        assert db_jobcard_2.created_at is not None
        assert db_jobcard_1.updated_at is None
        assert db_jobcard_2.updated_at is None
        assert (
            db_jobcard_1.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_jobcard_1.model_dump()
        )
        assert (
            db_jobcard_2.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_jobcard_2.model_dump()
        )
        assert len(db_jobcard_1.inventories) == 2
        assert len(db_jobcard_2.inventories) == 2

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter(
                    col(column_expression=InventoryJobCardLink.jobcard_id).in_(
                        [db_jobcard_1.id, db_jobcard_2.id]
                    )
                )
            )
        ).all()

        jobcard_inventory_quantity: dict[tuple[int, int], int] = {
            (link.jobcard_id, link.inventory_id): link.quantity
            for link in inventory_jobcard_links
        }

        assert inventory_jobcard_links is not None
        assert len(inventory_jobcard_links) == 4
        assert all(
            jobcard_inventory_quantity[(jobcard.id, inventory.id)]
            == quantities[f"jobcard_{idx + 1}"][inventory.id]
            for idx, jobcard in enumerate([db_jobcard_1, db_jobcard_2])
            for inventory in jobcard.inventories
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    inventory.id
                    for jobcard in [db_jobcard_1, db_jobcard_2]
                    for inventory in jobcard.inventories
                ],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_jobcard_by_id_single_inventory(self) -> None:
        """Retrieving a job card by ID single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Read job card by ID
        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=db_jobcard.id
        )

        assert result is not None
        assert result.model_dump() == db_jobcard.model_dump()
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_link: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_link is not None
        assert (
            inventory_jobcard_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert db_inventory.quantity == initial_quantity

    def test_read_jobcard_by_id_multiple_inventories(self) -> None:
        """Retrieving a job card by ID multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Read job card by ID
        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=db_jobcard.id
        )

        assert result is not None
        assert result.model_dump() == db_jobcard.model_dump()
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_jobcard_links, key=lambda x: x.inventory_id),
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
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_non_existent_jobcard(self) -> None:
        """Retrieving a non-existent job card."""
        non_existent_id: int = -1

        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session,
            record_id=non_existent_id,
        )

        assert result is None

    def test_read_multiple_jobcards_by_ids(self) -> None:
        """Retrieving multiple job cards by IDs."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple job cards
        result: Sequence[JobCard] = self.jobcard_view.create_multiple(
            db_session=self.session,
            records=[
                JobCard(
                    **self.test_jobcard_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                JobCard(
                    **self.test_jobcard_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        retrieved_jobcards: Sequence[JobCard] = (
            self.jobcard_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[j.id for j in result],
            )
        )

        assert len(retrieved_jobcards) == len(result)
        assert all(
            rj.model_dump() == j.model_dump()
            for rj, j in zip(retrieved_jobcards, result, strict=False)
        )
        assert all(
            inventory in jobcard.inventories
            for jobcard, inventory in zip(
                retrieved_jobcards,
                [self.test_inventory_1, self.test_inventory_2],
                strict=False,
            )
        )

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter(
                    col(column_expression=InventoryJobCardLink.jobcard_id).in_(
                        [jobcard.id for jobcard in retrieved_jobcards]
                    )
                )
            )
        ).all()

        jobcard_inventory_quantity: dict[tuple[int, int], int] = {
            (link.jobcard_id, link.inventory_id): link.quantity
            for link in inventory_jobcard_links
        }

        assert inventory_jobcard_links is not None
        assert len(inventory_jobcard_links) == 2
        assert all(
            jobcard_inventory_quantity[(jobcard.id, inventory.id)]
            == inventory._service_quantity
            for jobcard in retrieved_jobcards
            for inventory in jobcard.inventories
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    i.id for j in retrieved_jobcards for i in j.inventories
                ],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 2
        assert all(
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_read_all_jobcards(self) -> None:
        """Retrieving all job cards."""
        # Create multiple job cards
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )

        result: PaginationBase[JobCard] = self.jobcard_view.read_all(
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
                self.test_jobcard_1.description,
                self.test_jobcard_2.description,
            ]
            for j in result.records
        )

    def test_read_all_jobcards_pagination(self) -> None:
        """Job card pagination multiple pages."""
        # Create job cards to test pagination
        jobcard_1: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        jobcard_2: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        jobcard_3: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[JobCard] = self.jobcard_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == jobcard_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert all(
            j.description in [jobcard_1.description, jobcard_2.description]
            and j.description != jobcard_3.description
            for j in page1_result.records
        )

        # Test second page
        page2_result: PaginationBase[JobCard] = self.jobcard_view.read_all(
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
            j.description in [jobcard_3.description]
            and j.description
            not in [jobcard_1.description, jobcard_2.description]
            for j in page2_result.records
        )

    def test_search_jobcard_by_description(self) -> None:
        """Searching job cards by description."""
        # Create test job cards
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Search for job cards with specific description
        result: PaginationBase[JobCard] = self.jobcard_view.read_all(
            db_session=self.session,
            search_by="description",
            search_query="Job Card 1",
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
            j.description == self.test_jobcard_1.description
            for j in result.records
        )

    def test_search_jobcard_by_invalid_column(self) -> None:
        """Search job card by invalid column name."""
        # Create test job cards
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_2],
            ),
        )
        self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_3.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.read_all(
                db_session=self.session,
                search_by="invalid",
                search_query="Job Card 1",
            )

        assert "Invalid search column" in str(exc_info.value)

    def test_update_jobcard(self) -> None:
        """Updating a job card."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )

        # Update jobcard
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=db_jobcard.id,
            record=JobCard(
                **updated_jobcard.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_jobcard.model_dump()
        )
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_link: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_link is not None
        assert (
            inventory_jobcard_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert db_inventory.quantity == initial_quantity

    def test_update_jobcard_inventory_single_inventory(self) -> None:
        """Updating a job card single inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = 20

        # Update jobcard
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=db_jobcard.id,
            record=JobCard(
                **updated_jobcard.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_jobcard.model_dump()
        )
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_link: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_link is not None
        assert (
            inventory_jobcard_link[0].quantity
            == self.test_inventory_1._service_quantity
        )

        # Verify inventory quantity persists in inventory
        db_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert db_inventory is not None
        assert db_inventory.quantity == initial_quantity

    def test_update_jobcard_add_inventory(self) -> None:
        """Updating a job card by adding inventory item."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_2._service_quantity = 20

        # Update jobcard
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=db_jobcard.id,
            record=JobCard(
                **updated_jobcard.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_jobcard.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_jobcard_links, key=lambda x: x.inventory_id),
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
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_update_jobcard_remove_inventory(self) -> None:
        """Updating a job card by removing inventory item."""
        # Set inventory quantity
        initial_quantity: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )

        # Update jobcard
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=db_jobcard.id,
            record=JobCard(
                **updated_jobcard.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_jobcard.model_dump()
        )
        assert len(result.inventories) == 1
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 not in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_jobcard_links, key=lambda x: x.inventory_id),
                sorted([self.test_inventory_1], key=lambda x: x.id),
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
        assert len(db_inventories) == 1
        assert all(
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity],
                strict=True,
            )
        )

    def test_update_jobcard_non_existent_inventory(self) -> None:
        """Updating a job card with non-existent inventory item."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )

        inventory_id: int = -1

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.update_by_id(
                db_session=self.session,
                record_id=db_jobcard.id,
                record=JobCard(
                    **updated_jobcard.model_dump(),
                    inventories=[Inventory(id=inventory_id)],  # type: ignore
                ),
            )

        assert f"Inventory with id {inventory_id} not found" in str(
            exc_info.value
        )

    def test_update_jobcard_inventory_quantity_negative(self) -> None:
        """Updating a job card with negative inventory quantity."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = -1

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.update_by_id(
                db_session=self.session,
                record_id=db_jobcard.id,
                record=JobCard(
                    **updated_jobcard.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
            )

        assert (
            f"Service quantity for {self.test_inventory_1.item_name} "
            "must be at least 1" in str(exc_info.value)
        )

    def test_update_jobcard_multiple_inventories(self) -> None:
        """Updating a job card multiple inventory items."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        initial_quantity_2: int = self.test_inventory_2.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_1._service_quantity = 20
        self.test_inventory_2._service_quantity = 30

        # Update jobcard
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=db_jobcard.id,
            record=JobCard(
                **updated_jobcard.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == updated_jobcard.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=result.id
                )
            )
        ).all()

        assert inventory_jobcard_links is not None
        assert all(
            link.quantity == inventory._service_quantity
            for link, inventory in zip(
                sorted(inventory_jobcard_links, key=lambda x: x.inventory_id),
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
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1, initial_quantity_2],
                strict=True,
            )
        )

    def test_update_jobcard_inventory_quantity_exceeds_available_quantity(
        self,
    ) -> None:
        """Updating a job card required quantity exceeds available quantity."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_2._service_quantity = 200

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.update_by_id(
                db_session=self.session,
                record_id=db_jobcard.id,
                record=JobCard(
                    **updated_jobcard.model_dump(),
                    inventories=[self.test_inventory_1, self.test_inventory_2],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_2.item_name}. "
            f"Required: {self.test_inventory_2._service_quantity}, "
            f"Available: {self.test_inventory_2.quantity}"
            in str(exc_info.value)
        )

    def test_update_jobcard_inventory_quantity_exceeds_inventory_threshold(
        self,
    ) -> None:
        """Updating job card inventory quantity exceeds inventory threshold."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_2.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )
        self.test_inventory_2._service_quantity = 1000

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.update_by_id(
                db_session=self.session,
                record_id=db_jobcard.id,
                record=JobCard(
                    **updated_jobcard.model_dump(),
                    inventories=[self.test_inventory_1, self.test_inventory_2],
                ),
            )

        assert (
            f"Insufficient quantity for {self.test_inventory_2.item_name}. "
            f"Required: {self.test_inventory_2._service_quantity}, "
            f"Available: {self.test_inventory_2.quantity}"
            in str(exc_info.value)
        )

    def test_update_non_existent_jobcard(self) -> None:
        """Updating a non-existent job card."""
        non_existent_id: int = -1

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )

        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=JobCard(**updated_jobcard.model_dump()),
        )

        assert result is None

    def test_update_jobcard_no_inventory(self) -> None:
        """Updating a job card without inventory."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        db_jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        updated_jobcard: JobCardBase = JobCardBase(
            status=ServiceStatus.IN_PROGRESS,
            service_date=date.today() + timedelta(days=1),
            description="Updated Test Job Card",
            vehicle_id=self.test_vehicle_1.id,
        )

        with pytest.raises(expected_exception=ValueError) as exc_info:
            self.jobcard_view.update_by_id(
                db_session=self.session,
                record_id=db_jobcard.id,
                record=JobCard(**updated_jobcard.model_dump()),
            )

        assert "At least one inventory item is required" in str(exc_info.value)

    def test_update_multiple_jobcards(self) -> None:
        """Updating multiple job cards."""
        # Set inventory quantity
        initial_quantity_1: int = self.test_inventory_1.quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple job cards
        result: Sequence[JobCard] = self.jobcard_view.create_multiple(
            db_session=self.session,
            records=[
                JobCard(
                    **self.test_jobcard_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                JobCard(
                    **self.test_jobcard_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        updated_jobcards: Sequence[JobCardBase] = [
            JobCardBase(
                status=ServiceStatus.IN_PROGRESS,
                service_date=date.today() + timedelta(days=1),
                description="Updated Test Job Card",
                vehicle_id=self.test_vehicle_1.id,
            )
            for _ in result
        ]

        # Update multiple job cards
        updated_result: Sequence[JobCard] = (
            self.jobcard_view.update_multiple_by_ids(
                db_session=self.session,
                records=[
                    JobCard(
                        **updated_jobcard.model_dump(),
                        inventories=[self.test_inventory_1],
                    )
                    for updated_jobcard in updated_jobcards
                ],
                record_ids=[j.id for j in result],
            )
        )

        assert len(updated_result) == len(result)
        assert all(j.created_at is not None for j in updated_result)
        assert all(j.updated_at is not None for j in updated_result)
        assert all(j.updated_at is not None for j in updated_result)
        assert all(
            j.model_dump(exclude={"id", "created_at", "updated_at"})
            == u.model_dump()
            for j, u in zip(updated_result, updated_jobcards, strict=False)
        )
        assert all(len(j.inventories) == 1 for j in updated_result)
        assert all(
            j.inventories[0] == result[idx].inventories[0]
            for idx, j in enumerate(updated_result)
        )

        # Verify inventory quantity in inventory-jobcard links
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter(
                    col(column_expression=InventoryJobCardLink.jobcard_id).in_(
                        [jobcard.id for jobcard in result]
                    )
                )
            )
        ).all()

        jobcard_inventory_quantity: dict[tuple[int, int], int] = {
            (link.jobcard_id, link.inventory_id): link.quantity
            for link in inventory_jobcard_links
        }

        assert inventory_jobcard_links is not None
        assert len(inventory_jobcard_links) == 2
        assert all(
            jobcard_inventory_quantity[(jobcard.id, inventory.id)]
            == inventory._service_quantity
            for jobcard in updated_result
            for inventory in jobcard.inventories
        )

        # Verify inventories quantity persists in inventory
        db_inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    inventory.id
                    for jobcard in result
                    for inventory in jobcard.inventories
                ],
            )
        )

        assert db_inventories is not None
        assert len(db_inventories) == 1
        assert all(
            db_inventory.quantity == quantity
            for db_inventory, quantity in zip(
                sorted(db_inventories, key=lambda x: x.id),
                [initial_quantity_1],
                strict=True,
            )
        )

    def test_delete_jobcard(self) -> None:
        """Deleting a job card."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10

        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        result: Message | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert result is not None
        assert result == Message(message="Record deleted successfully")

        # Verify job card no longer exists
        retrieved_jobcard: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert retrieved_jobcard is None

        # Verify inventory no longer linked to job card
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter_by(
                    jobcard_id=jobcard.id
                )
            )
        ).all()

        assert inventory_jobcard_links == []

    def test_delete_non_existent_jobcard(self) -> None:
        """Deleting a non-existent job card."""
        non_existent_id: int = -1

        result: Message | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_delete_multiple_jobcards_by_ids(self) -> None:
        """Deleting multiple job cards by IDs."""
        # Set inventory quantity
        self.test_inventory_1._service_quantity = 10
        self.test_inventory_2._service_quantity = 20

        # Create multiple job cards
        jobcards: Sequence[JobCard] = self.jobcard_view.create_multiple(
            db_session=self.session,
            records=[
                JobCard(
                    **self.test_jobcard_1.model_dump(),
                    inventories=[self.test_inventory_1],
                ),
                JobCard(
                    **self.test_jobcard_2.model_dump(),
                    inventories=[self.test_inventory_2],
                ),
            ],
        )

        result: Message | None = self.jobcard_view.delete_multiple_by_ids(
            db_session=self.session, record_ids=[j.id for j in jobcards]
        )

        assert result is not None
        assert result == Message(message="Records deleted successfully")

        # Verify job cards no longer exist
        retrieved_jobcards: Sequence[JobCard] = (
            self.jobcard_view.read_multiple_by_ids(
                db_session=self.session, record_ids=[j.id for j in jobcards]
            )
        )

        assert len(retrieved_jobcards) == 0

        # Verify inventory no longer linked to job card
        inventory_jobcard_links: Sequence[InventoryJobCardLink] = (
            self.session.exec(
                statement=select(InventoryJobCardLink).filter(
                    col(column_expression=InventoryJobCardLink.jobcard_id).in_(
                        [j.id for j in jobcards]
                    )
                )
            )
        ).all()

        assert inventory_jobcard_links == []

        # Verify inventories still exist
        inventories: Sequence[Inventory] = (
            self.inventory_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[
                    self.test_inventory_1.id,
                    self.test_inventory_2.id,
                ],
            )
        )

        assert len(inventories) == 2
        assert any(i.id == self.test_inventory_1.id for i in inventories)
        assert any(i.id == self.test_inventory_2.id for i in inventories)
        assert all(len(i.jobcards) == 0 for i in inventories)
