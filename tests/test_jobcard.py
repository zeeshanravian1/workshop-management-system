"""JobCard Test Cases.

Description:
- This file contains test cases for job card operations.

"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber

from tests.conftest import TestSetup
from workshop_management_system.core.config import (
    InventoryCategory,
    ServiceStatus,
)
from workshop_management_system.v1.base.model import PaginationBase
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView
from workshop_management_system.v1.inventory.model import (
    Inventory,
    InventoryBase,
)
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.jobcard.model import JobCard, JobCardBase
from workshop_management_system.v1.jobcard.view import JobCardView
from workshop_management_system.v1.supplier.model import Supplier, SupplierBase
from workshop_management_system.v1.supplier.view import SupplierView
from workshop_management_system.v1.vehicle.model import Vehicle, VehicleBase
from workshop_management_system.v1.vehicle.view import VehicleView


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
            quantity=10,
            unit_price=100,
            minimum_threshold=5,
            category=InventoryCategory.ELECTRICALS,
        )
        inventory_2: InventoryBase = InventoryBase(
            item_name="Test Item 2",
            quantity=20,
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
        with pytest.raises(ValidationError) as exc_info:
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
        with pytest.raises(ValidationError) as exc_info:
            JobCardBase(
                status=ServiceStatus.PENDING,
                service_date="Invalid Date",  # type: ignore
                description="Test Job Card",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Input should be a valid date or datetime" in str(
            exc_info.value
        )

        # Check if date is in the past
        with pytest.raises(ValidationError) as exc_info:
            JobCardBase(
                status=ServiceStatus.PENDING,
                service_date=date.today() - timedelta(days=1),
                description="Test Job Card",
                vehicle_id=self.test_vehicle_1.id,
            )

        assert "Service date cannot be in the past" in str(exc_info.value)

    def test_create_jobcard(self) -> None:
        """Creating a job card."""
        result: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(**self.test_jobcard_1.model_dump()),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "vehicle"}
            )
            == self.test_jobcard_1.model_dump()
        )
        assert result.vehicle == self.test_vehicle_1

    def test_create_jobcard_with_single_inventory(self) -> None:
        """Creating a job card with single inventory item."""
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
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "inventories"}
            )
            == self.test_jobcard_1.model_dump()
        )
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

    def test_create_jobcard_with_multiple_inventories(self) -> None:
        """Creating a job card with multiple inventory items."""
        # Create job card
        result: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "inventories"}
            )
            == self.test_jobcard_1.model_dump()
        )
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

    def test_read_jobcard_by_id_with_single_inventory(self) -> None:
        """Retrieving a job card by ID with single inventory item."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session,
            record_id=jobcard.id,
        )

        assert result is not None
        assert jobcard.model_dump() == result.model_dump()
        assert len(result.inventories) == 1
        assert result.inventories[0] == self.test_inventory_1

    def test_read_jobcard_by_id_with_multiple_inventories(self) -> None:
        """Retrieving a job card by ID with multiple inventory items."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session,
            record_id=jobcard.id,
        )

        assert result is not None
        assert jobcard.model_dump() == result.model_dump()
        assert len(result.inventories) == 2
        assert self.test_inventory_1 in result.inventories
        assert self.test_inventory_2 in result.inventories

    def test_read_non_existent_jobcard(self) -> None:
        """Retrieving a non-existent job card."""
        non_existent_id: int = -1
        result: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session,
            record_id=non_existent_id,
        )

        assert result is None

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
        assert any(
            j.description == self.test_jobcard_1.description
            for j in result.records
        )
        assert any(
            j.description == self.test_jobcard_2.description
            for j in result.records
        )

    def test_read_all_jobcards_pagination(self) -> None:
        """Job card pagination with multiple pages."""
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
        assert any(
            j.description == jobcard_1.description
            for j in page1_result.records
        )
        assert any(
            j.description == jobcard_2.description
            for j in page1_result.records
        )
        assert all(
            j.description != jobcard_3.description
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
        assert any(
            j.description == jobcard_3.description
            for j in page2_result.records
        )
        assert all(
            j.description != jobcard_1.description
            for j in page2_result.records
        )
        assert all(
            j.description != jobcard_2.description
            for j in page2_result.records
        )

    def test_update_jobcard(self) -> None:
        """Updating a job card."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Update job card
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=jobcard.id,
            record=JobCard(**self.test_jobcard_2.model_dump()),
        )

        assert result is not None
        assert result.id == jobcard.id
        assert result.model_dump() == jobcard.model_dump()

    def test_update_non_existent_jobcard(self) -> None:
        """Updating a non-existent job card."""
        non_existent_id: int = -1
        result: JobCard | None = self.jobcard_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=JobCard(**self.test_jobcard_2.model_dump()),
        )

        assert result is None

    def test_update_jobcard_inventory_with_single_inventory(self) -> None:
        """Updating a job card with single inventory item."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=jobcard.id,
            previous_inventory_id=self.test_inventory_1.id,
            new_inventory_id=self.test_inventory_2.id,
        )

        assert result is not None
        assert result.id == jobcard.id
        assert len(result.inventories) == 1
        assert self.test_inventory_2 in result.inventories
        assert self.test_inventory_1 not in result.inventories

    def test_update_jobcard_inventory_with_multiple_inventories(self) -> None:
        """Updating a job card with multiple inventory items."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1, self.test_inventory_2],
            ),
        )

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=jobcard.id,
            previous_inventory_id=self.test_inventory_1.id,
            new_inventory_id=self.test_inventory_3.id,
        )

        assert result is not None
        assert result.id == jobcard.id
        assert len(result.inventories) == 2
        assert self.test_inventory_2 in result.inventories
        assert self.test_inventory_3 in result.inventories
        assert self.test_inventory_1 not in result.inventories

    def test_update_jobcard_inventory_with_non_existent_jobcard(self) -> None:
        """Updating a non-existent job card with inventory item."""
        non_existent_id: int = -1

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=non_existent_id,
            previous_inventory_id=self.test_inventory_1.id,
            new_inventory_id=self.test_inventory_2.id,
        )

        assert result is None

    def test_update_jobcard_inventory_with_non_existent_previous_inventory(
        self,
    ) -> None:
        """Updating a job card with non-existent inventory item."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        non_existent_inventory_id: int = -1

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=jobcard.id,
            previous_inventory_id=non_existent_inventory_id,
            new_inventory_id=self.test_inventory_2.id,
        )

        assert result is None

        # Verify original inventory relationship remains unchanged
        db_record: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert db_record is not None
        assert len(db_record.inventories) == 1
        assert self.test_inventory_1 in db_record.inventories

    def test_update_jobcard_inventory_with_non_existent_new_inventory(
        self,
    ) -> None:
        """Updating a job card with non-existent new inventory item."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        non_existent_inventory_id: int = -1

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=jobcard.id,
            previous_inventory_id=self.test_inventory_1.id,
            new_inventory_id=non_existent_inventory_id,
        )

        assert result is None

        # Verify original inventory relationship remains unchanged
        db_record: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert db_record is not None
        assert len(db_record.inventories) == 1
        assert self.test_inventory_1 in db_record.inventories

    def test_update_jobcard_inventory_with_wrong_previous_inventory(
        self,
    ) -> None:
        """Updating a job card with wrong previous inventory item."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Update inventory
        result: JobCard | None = self.jobcard_view.update_inventory(
            db_session=self.session,
            record_id=jobcard.id,
            previous_inventory_id=self.test_inventory_2.id,
            new_inventory_id=self.test_inventory_2.id,
        )

        assert result is None

        # Verify original inventory relationship remains unchanged
        db_record: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert db_record is not None
        assert len(db_record.inventories) == 1
        assert self.test_inventory_1 in db_record.inventories

    def test_delete_jobcard(self) -> None:
        """Deleting a job card."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        result: JobCard | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert result is not None
        assert result.id == jobcard.id

        # Verify job card no longer exists
        retrieved_jobcard: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert retrieved_jobcard is None

    def test_delete_non_existent_jobcard(self) -> None:
        """Deleting a non-existent job card."""
        non_existent_id: int = -1

        result: JobCard | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_delete_multiple_jobcards_with_shared_inventory(self) -> None:
        """Deleting multiple job cards with shared inventory."""
        # Create job cards
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
                inventories=[self.test_inventory_1],
            ),
        )

        # Delete first job card
        result_1: JobCard | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=jobcard_1.id
        )

        assert result_1 is not None
        assert result_1.id == jobcard_1.id

        # Verify first job card no longer exists
        retrieved_jobcard_1: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard_1.id
        )

        assert retrieved_jobcard_1 is None

        # Verify second job card still exists
        retrieved_jobcard_2: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard_2.id
        )

        assert retrieved_jobcard_2 is not None
        assert retrieved_jobcard_2.id == jobcard_2.id

        # Verify inventory still exists
        inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert inventory is not None
        assert inventory.id == self.test_inventory_1.id

        # Delete second job card
        result_2: JobCard | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=jobcard_2.id
        )

        assert result_2 is not None
        assert result_2.id == jobcard_2.id

        # Verify second job card no longer exists
        retrieved_jobcard2: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard_2.id
        )

        assert retrieved_jobcard2 is None

        # Verify inventory still exists
        retrieved_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert retrieved_inventory is not None
        assert retrieved_inventory.id == self.test_inventory_1.id

    def test_delete_jobcard_verify_inventory_links_deleted(self) -> None:
        """Verifying inventory links are deleted on job card delete."""
        # Create job card
        jobcard: JobCard = self.jobcard_view.create(
            db_session=self.session,
            record=JobCard(
                **self.test_jobcard_1.model_dump(),
                inventories=[self.test_inventory_1],
            ),
        )

        # Delete job card
        result: JobCard | None = self.jobcard_view.delete_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert result is not None
        assert result.id == jobcard.id

        # Verify job card no longer exists
        retrieved_jobcard: JobCard | None = self.jobcard_view.read_by_id(
            db_session=self.session, record_id=jobcard.id
        )

        assert retrieved_jobcard is None

        # Verify inventory no longer linked to job card
        inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=self.test_inventory_1.id
        )

        assert inventory is not None
        assert inventory.id == self.test_inventory_1.id
        assert len(inventory.jobcards) == 0
