"""Vehicle Test Cases.

Description:
- This file contains test cases for vehicle operations.

"""

from collections.abc import Sequence

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.exc import IntegrityError

from tests.conftest import TestSetup
from workshop_management_system.v1.base.model import Message, PaginationBase
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView
from workshop_management_system.v1.vehicle.model import Vehicle, VehicleBase
from workshop_management_system.v1.vehicle.view import VehicleView


class TestVehicle(TestSetup):
    """Test cases for vehicle operations.

    Description:
    - This class provides test cases for vehicle operations.

    Attributes:
    - `customer_view` (CustomerView): An instance of CustomerView class.
    - `test_customer` (Customer): An instance of Customer class for validation.
    - `vehicle_view` (VehicleView): An instance of VehicleView class.
    - `test_vehicle_1` (VehicleBase): An instance of VehicleBase class for
    validation.
    - `test_vehicle_2` (VehicleBase): An instance of VehicleBase class for
    validation.

    """

    customer_view: CustomerView
    test_customer_1: Customer
    test_customer_2: Customer
    vehicle_view: VehicleView
    test_vehicle_1: VehicleBase
    test_vehicle_2: VehicleBase
    test_vehicle_3: VehicleBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.customer_view = CustomerView(Customer)
        self.vehicle_view = VehicleView(Vehicle)

        # Create customer instances for validation
        customer_1: CustomerBase = CustomerBase(
            name="Test Customer 1",
            email="test1@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address 1",
        )
        customer_2: CustomerBase = CustomerBase(
            name="Test Customer 2",
            email="test2@example.com",
            contact_no=PhoneNumber("+923011234567"),
            address="Test Address 2",
        )

        # Create customers
        self.test_customer_1 = self.customer_view.create(
            db_session=self.session,
            record=Customer(**customer_1.model_dump()),
        )
        self.test_customer_2 = self.customer_view.create(
            db_session=self.session,
            record=Customer(**customer_2.model_dump()),
        )

        # Setup test vehicles
        self.test_vehicle_1 = VehicleBase(
            make="Toyota",
            model="Corolla",
            year=2020,
            vehicle_number="ABC-1234",
            customer_id=self.test_customer_1.id,
        )
        self.test_vehicle_2 = VehicleBase(
            make="Honda",
            model="Civic",
            year=2021,
            vehicle_number="DEF-4567",
            customer_id=self.test_customer_2.id,
        )
        self.test_vehicle_3 = VehicleBase(
            make="Suzuki",
            model="Swift",
            year=2022,
            vehicle_number="GHI-8901",
            customer_id=self.test_customer_1.id,
        )

    def test_year_validation(self) -> None:
        """Validating vehicle year."""
        with pytest.raises(ValidationError) as exc_info:
            VehicleBase(
                make="Toyota",
                model="Corolla",
                year=1885,
                vehicle_number="ABC-1234",
                customer_id=self.test_customer_1.id,
            )

        assert "Input should be greater than or equal to 1886" in str(
            exc_info.value
        )

    def test_duplicate_vehicle_number_validation(self) -> None:
        """Validating duplicate vehicle number."""
        # Create first vehicle
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        # Create second vehicle with same vehicle number
        duplicate_vehicle = VehicleBase(
            make="Honda",
            model="City",
            year=2022,
            vehicle_number=self.test_vehicle_1.vehicle_number,
            customer_id=self.test_customer_1.id,
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.vehicle_view.create(
                db_session=self.session,
                record=Vehicle(**duplicate_vehicle.model_dump()),
            )

        assert "UNIQUE constraint failed: vehicle.vehicle_number" in str(
            exc_info.value
        )

    def test_create_vehicle(self) -> None:
        """Creating a vehicle."""
        result: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "customer"}
            )
            == self.test_vehicle_1.model_dump()
        )
        assert result.customer == self.test_customer_1

    def test_create_multiple_vehicles(self) -> None:
        """Creating multiple vehicles."""
        # Create multiple test vehicles
        result: Sequence[Vehicle] = self.vehicle_view.create_multiple(
            db_session=self.session,
            records=[
                Vehicle(**self.test_vehicle_1.model_dump()),
                Vehicle(**self.test_vehicle_2.model_dump()),
            ],
        )

        # Verify vehicles are created
        assert len(result) == 2
        assert all(v.id is not None for v in result)
        assert all(v.created_at is not None for v in result)
        assert all(v.updated_at is None for v in result)
        assert all(
            v.model_dump(
                exclude={"id", "created_at", "updated_at", "customer"}
            )
            in [
                self.test_vehicle_1.model_dump(),
                self.test_vehicle_2.model_dump(),
            ]
            for v in result
        )

    def test_read_vehicle_by_id(self) -> None:
        """Retrieving a vehicle by ID."""
        # Create vehicle
        vehicle: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        result: Vehicle | None = self.vehicle_view.read_by_id(
            db_session=self.session,
            record_id=vehicle.id,
        )

        assert result is not None
        assert vehicle.model_dump() == result.model_dump()
        assert result.customer == self.test_customer_1

    def test_read_non_existent_vehicle(self) -> None:
        """Retrieving a non-existent vehicle."""
        non_existent_id: int = -1
        result: Vehicle | None = self.vehicle_view.read_by_id(
            db_session=self.session,
            record_id=non_existent_id,
        )

        assert result is None

    def test_read_multiple_vehicles_by_ids(self) -> None:
        """Retrieving multiple vehicles by ID."""
        # Create multiple test vehicles
        vehicle_1: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )
        vehicle_2: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )

        # Retrieve multiple vehicles by ID
        retrieved_vehicles: Sequence[Vehicle] = (
            self.vehicle_view.read_multiple_by_ids(
                db_session=self.session,
                record_ids=[vehicle_1.id, vehicle_2.id],
            )
        )

        assert len(retrieved_vehicles) == 2
        assert all(
            rv.model_dump() == v.model_dump()
            for rv, v in zip(
                retrieved_vehicles, [vehicle_1, vehicle_2], strict=False
            )
        )

    def test_read_all_vehicles(self) -> None:
        """Retrieving all vehicles."""
        # Create multiple test vehicles
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )

        result: PaginationBase[Vehicle] = self.vehicle_view.read_all(
            db_session=self.session,
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
            v.vehicle_number == self.test_vehicle_1.vehicle_number
            for v in result.records
        )
        assert any(
            v.vehicle_number == self.test_vehicle_2.vehicle_number
            for v in result.records
        )

    def test_read_all_vehicles_pagination(self) -> None:
        """Vehicle pagination with multiple pages."""
        # Create test vehicles to test pagination
        vehicle_1: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )
        vehicle_2: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )
        vehicle_3: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_3.model_dump()),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[Vehicle] = self.vehicle_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == vehicle_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert any(
            v.vehicle_number == vehicle_1.vehicle_number
            for v in page1_result.records
        )
        assert any(
            v.vehicle_number == vehicle_2.vehicle_number
            for v in page1_result.records
        )
        assert all(
            v.vehicle_number != vehicle_3.vehicle_number
            for v in page1_result.records
        )

        # Test second page
        page2_result: PaginationBase[Vehicle] = self.vehicle_view.read_all(
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
            v.vehicle_number == vehicle_3.vehicle_number
            for v in page2_result.records
        )
        assert all(
            v.vehicle_number != vehicle_1.vehicle_number
            for v in page2_result.records
        )
        assert all(
            v.vehicle_number != vehicle_2.vehicle_number
            for v in page2_result.records
        )

    def test_search_vehicle_by_vehicle_number(self) -> None:
        """Searching vehicles by vehicle number."""
        # Create test vehicles
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_3.model_dump()),
        )

        # Search for vehicles with specific vehicle number
        result: PaginationBase[Vehicle] = self.vehicle_view.read_all(
            db_session=self.session,
            search_by="vehicle_number",
            search_query="ABC",
        )

        assert result.total_records == 1
        assert (
            result.records[0].vehicle_number
            == self.test_vehicle_1.vehicle_number
        )

    def test_search_vehicle_by_invalid_column(self) -> None:
        """Search vehicle by invalid column name."""
        # Create test vehicles
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )
        self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_3.model_dump()),
        )

        with pytest.raises(ValueError) as exc_info:
            self.vehicle_view.read_all(
                db_session=self.session,
                search_by="invalid",
                search_query="ABC",
            )

        assert "Invalid search column" in str(exc_info.value)

    def test_update_vehicle(self) -> None:
        """Updating a vehicle."""
        # Create vehicle
        vehicle: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        # Update vehicle
        result: Vehicle | None = self.vehicle_view.update_by_id(
            db_session=self.session,
            record_id=vehicle.id,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )

        assert result is not None
        assert result.id == vehicle.id
        assert result.model_dump() == vehicle.model_dump()

    def test_update_non_existent_vehicle(self) -> None:
        """Updating a non-existent vehicle."""
        non_existent_id: int = -1
        result: Vehicle | None = self.vehicle_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )

        assert result is None

    def update_duplicate_vehicle_number(self) -> None:
        """Updating a vehicle with duplicate vehicle number."""
        # Create first vehicle
        vehicle_1: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        # Create second vehicle
        vehicle_2: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_2.model_dump()),
        )

        # Update vehicle 2 with vehicle number of vehicle 1
        vehicle_2.vehicle_number = vehicle_1.vehicle_number

        with pytest.raises(IntegrityError) as exc_info:
            self.vehicle_view.update_by_id(
                db_session=self.session,
                record_id=vehicle_2.id,
                record=vehicle_2,
            )

        assert "UNIQUE constraint failed: vehicle.vehicle_number" in str(
            exc_info.value
        )

    def test_update_multiple_vehicles_by_ids(self) -> None:
        """Updating multiple vehicles."""
        # Create multiple test vehicles
        vehicles: Sequence[Vehicle] = self.vehicle_view.create_multiple(
            db_session=self.session,
            records=[
                Vehicle(**self.test_vehicle_1.model_dump()),
                Vehicle(**self.test_vehicle_2.model_dump()),
            ],
        )

        vehicle_1: VehicleBase = VehicleBase(
            make="Toyota",
            model="Corolla",
            year=2021,
            vehicle_number="XYZ-1234",
            customer_id=self.test_customer_1.id,
        )
        vehicle_2: VehicleBase = VehicleBase(
            make="Honda",
            model="Civic",
            year=2022,
            vehicle_number="PQR-4567",
            customer_id=self.test_customer_2.id,
        )

        # Update multiple vehicles
        updated_vehicles: Sequence[Vehicle] = (
            self.vehicle_view.update_multiple_by_ids(
                db_session=self.session,
                record_ids=[v.id for v in vehicles],
                records=[
                    Vehicle(**vehicle_1.model_dump()),
                    Vehicle(**vehicle_2.model_dump()),
                ],
            )
        )

        # Verify vehicles are updated
        assert len(updated_vehicles) == 2
        assert all(v.id is not None for v in updated_vehicles)
        assert all(v.created_at is not None for v in updated_vehicles)
        assert all(v.updated_at is not None for v in updated_vehicles)
        assert all(
            v.model_dump(
                exclude={"id", "created_at", "updated_at", "customer"}
            )
            in [vehicle_1.model_dump(), vehicle_2.model_dump()]
            for v in updated_vehicles
        )

    def test_delete_vehicle(self) -> None:
        """Deleting a vehicle."""
        # Create vehicle
        vehicle: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        # Delete vehicle
        deleted_vehicle: Message | None = self.vehicle_view.delete_by_id(
            db_session=self.session,
            record_id=vehicle.id,
        )

        assert deleted_vehicle is not None
        assert deleted_vehicle == Message(
            message="Record deleted successfully"
        )

        # Verify vehicle no longer exists
        result: Vehicle | None = self.vehicle_view.read_by_id(
            db_session=self.session,
            record_id=vehicle.id,
        )

        assert result is None

        # Verify customer still exists
        customer: Customer | None = self.customer_view.read_by_id(
            db_session=self.session,
            record_id=self.test_customer_1.id,
        )
        assert customer is not None
        assert customer.id == self.test_customer_1.id

    def test_delete_non_existent_vehicle(self) -> None:
        """Deleting a non-existent vehicle."""
        non_existent_id: int = -1
        result: Message | None = self.vehicle_view.delete_by_id(
            db_session=self.session,
            record_id=non_existent_id,
        )

        assert result is None

    def test_cascade_delete_with_customer(self) -> None:
        """Verifying cascade delete when customer is deleted."""
        # Create vehicle
        vehicle: Vehicle = self.vehicle_view.create(
            db_session=self.session,
            record=Vehicle(**self.test_vehicle_1.model_dump()),
        )

        # Delete customer
        deleted_customer: Message | None = self.customer_view.delete_by_id(
            db_session=self.session,
            record_id=self.test_customer_1.id,
        )

        assert deleted_customer is not None
        assert deleted_customer == Message(
            message="Record deleted successfully"
        )

        # Verify vehicle is also deleted
        result: Vehicle | None = self.vehicle_view.read_by_id(
            db_session=self.session,
            record_id=vehicle.id,
        )
        assert result is None

    def test_delete_multiple_vehicles_by_ids(self) -> None:
        """Deleting multiple vehicles."""
        # Create multiple test vehicles
        vehicles: Sequence[Vehicle] = self.vehicle_view.create_multiple(
            db_session=self.session,
            records=[
                Vehicle(**self.test_vehicle_1.model_dump()),
                Vehicle(**self.test_vehicle_2.model_dump()),
            ],
        )

        result: Message | None = self.vehicle_view.delete_multiple_by_ids(
            db_session=self.session, record_ids=[v.id for v in vehicles]
        )

        assert result is not None
        assert result == Message(message="Records deleted successfully")

        # Verify vehicles no longer exist
        retrieved_vehicles: Sequence[Vehicle] = (
            self.vehicle_view.read_multiple_by_ids(
                db_session=self.session, record_ids=[v.id for v in vehicles]
            )
        )

        assert len(retrieved_vehicles) == 0
