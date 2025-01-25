"""Customer CRUD Test Cases.

Description:
- This file contains test cases for Customer CRUD operations.

"""

from collections.abc import Sequence
from uuid import UUID, uuid4

from tests.conftest import TestSetup
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


class TestCustomer(TestSetup):
    """Test cases for Customer CRUD operations.

    Description:
    - This class provides test cases for Customer CRUD operations.

    Attributes:
    - `customer_view` (CustomerView): An instance of CustomerView class.
    - `test_customer1` (Customer): An instance of Customer class.
    - `test_customer2` (Customer): An instance of Customer class.

    """

    customer_view: CustomerView
    test_customer1: Customer
    test_customer2: Customer

    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.customer_view = CustomerView(Customer)
        self.test_customer1 = Customer(
            name="Test User 1",
            mobile_number="1234567890",
            vehicle_registration_number="TEST123",
            email="test1@example.com",
            address="Test Address 1",
        )
        self.test_customer2 = Customer(
            name="Test User 2",
            mobile_number="9876543210",
            vehicle_registration_number="TEST456",
            email="test2@example.com",
            address="Test Address 2",
        )

    def test_create_customer(self) -> None:
        """Test case for creating a customer."""
        created_customer: Customer = self.customer_view.create(
            db_session=self.session, record=self.test_customer1
        )

        assert created_customer.id is not None
        assert created_customer.name == self.test_customer1.name
        assert created_customer.email == self.test_customer1.email

    def test_read_customer_by_id(self) -> None:
        """Test case for retrieving a customer by ID."""
        created_customer: Customer = self.customer_view.create(
            db_session=self.session, record=self.test_customer1
        )

        retrieved_customer: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=created_customer.id
        )

        assert retrieved_customer is not None
        assert retrieved_customer.id == created_customer.id
        assert retrieved_customer.name == self.test_customer1.name
        assert retrieved_customer.email == self.test_customer1.email

    def test_read_non_existent_customer(self) -> None:
        """Test case for retrieving a non-existent customer."""
        non_existent_id: UUID = uuid4()
        customer: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert customer is None

    def test_read_all_customers(self) -> None:
        """Test case for retrieving all customers."""
        # Create multiple test customers
        self.customer_view.create(
            db_session=self.session, record=self.test_customer1
        )
        self.customer_view.create(
            db_session=self.session, record=self.test_customer2
        )

        customers: Sequence[Customer] = self.customer_view.read_all(
            db_session=self.session
        )

        assert len(customers) == 2
        assert any(c.email == "test1@example.com" for c in customers)
        assert any(c.email == "test2@example.com" for c in customers)

    def test_update_customer(self) -> None:
        """Test case for updating a customer."""
        created_customer: Customer = self.customer_view.create(
            db_session=self.session, record=self.test_customer1
        )

        updated_data: Customer = Customer(
            name="Updated Name",
            email="updated@example.com",
            mobile_number="9999999999",
            vehicle_registration_number="UPD123",
            address="Updated Address",
        )

        result: Customer | None = self.customer_view.update(
            db_session=self.session,
            record_id=created_customer.id,
            record=updated_data,
        )

        assert result is not None
        assert result.name == updated_data.name
        assert result.email == updated_data.email
        assert result.mobile_number == updated_data.mobile_number

    def test_update_non_existent_customer(self) -> None:
        """Test case for updating a non-existent customer."""
        non_existent_id: UUID = uuid4()

        result: Customer | None = self.customer_view.update(
            db_session=self.session,
            record_id=non_existent_id,
            record=self.test_customer1,
        )

        assert result is None

    def test_delete_customer(self) -> None:
        """Test case for deleting a customer."""
        created_customer: Customer = self.customer_view.create(
            db_session=self.session, record=self.test_customer1
        )

        deleted_customer: Customer | None = self.customer_view.delete(
            db_session=self.session, record_id=created_customer.id
        )

        assert deleted_customer is not None
        assert deleted_customer.id == created_customer.id

        # Verify customer no longer exists
        retrieved_customer: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=created_customer.id
        )
        assert retrieved_customer is None

    def test_delete_non_existent_customer(self) -> None:
        """Test case for deleting a non-existent customer."""
        non_existent_id: UUID = uuid4()
        result: Customer | None = self.customer_view.delete(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None
