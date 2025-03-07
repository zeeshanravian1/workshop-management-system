"""Customer Test Cases.

Description:
- This file contains test cases for customer operations.

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


class TestCustomer(TestSetup):
    """Test cases for customer operations.

    Description:
    - This class provides test cases for customer operations.

    Attributes:
    - `customer_view` (CustomerView): An instance of CustomerView class.
    - `test_customer_1` (CustomerBase): An instance of CustomerBase class for
    validation.
    - `test_customer_2` (CustomerBase): An instance of CustomerBase class for
    validation.

    """

    customer_view: CustomerView
    test_customer_1: CustomerBase
    test_customer_2: CustomerBase
    test_customer_3: CustomerBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.customer_view = CustomerView(Customer)
        self.test_customer_1 = CustomerBase(
            name="Test Customer 1",
            email="test1@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address 1",
        )
        self.test_customer_2 = CustomerBase(
            name="Test Customer 2",
            email="test2@example.com",
            contact_no=PhoneNumber("+923011234567"),
            address="Test Address 2",
        )
        self.test_customer_3 = CustomerBase(
            name="Test Customer 3",
            email="test3@email.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address 3",
        )

    def test_create_customer(self) -> None:
        """Creating a customer."""
        result: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_customer_1.model_dump()
        )

    def test_duplicate_email_validation(self) -> None:
        """Validating duplicate email."""
        # Create first customer
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        # Create second customer with same email but different phone
        duplicate_email_customer: CustomerBase = CustomerBase(
            name="Test Customer",
            email="test1@example.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.customer_view.create(
                db_session=self.session,
                record=Customer(**duplicate_email_customer.model_dump()),
            )

        assert "UNIQUE constraint failed: customer.email" in str(
            exc_info.value
        )

    def test_invalid_email_validation(self) -> None:
        """Validating invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerBase(
                name="Test Customer",
                email="invalid.email@",
                contact_no=PhoneNumber("+923021234567"),
                address="Test Address",
            )

        assert "value is not a valid email address" in str(exc_info.value)

    def test_email_spaces_handling(self) -> None:
        """Handling spaces in email during creation."""
        customer_with_spaces: CustomerBase = CustomerBase(
            name="Test Customer",
            email="   test.spaces@example.com   ",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address",
        )

        result: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**customer_with_spaces.model_dump()),
        )

        if result.email and customer_with_spaces.email:
            assert " " not in str(result.email)
            assert str(result.email) == str(customer_with_spaces.email).strip()
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == customer_with_spaces.model_dump()
        )

    def test_duplicate_contact_no_validation(self) -> None:
        """Validating duplicate contact number."""
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        # Create second customer with same contact number but different email
        duplicate_contact_no_customer: CustomerBase = CustomerBase(
            name="Test Customer",
            email="test@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.customer_view.create(
                db_session=self.session,
                record=Customer(**duplicate_contact_no_customer.model_dump()),
            )

        assert "UNIQUE constraint failed: customer.contact_no" in str(
            exc_info.value
        )

    def test_invalid_contact_no_validation(self) -> None:
        """Validating invalid contact number format."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerBase(
                name="Test Customer",
                email="test@example.com",
                contact_no=PhoneNumber("1234567890"),
                address="Test Address",
            )

        assert "value is not a valid phone number" in str(exc_info.value)

        # Test with wrong country code
        with pytest.raises(ValidationError) as exc_info:
            CustomerBase(
                name="Test Customer",
                email="test@example.com",
                contact_no=PhoneNumber("+123001234567"),
                address="Test Address",
            )

        assert "value is not a valid phone number" in str(exc_info.value)

    def test_contact_no_spaces_handling(self) -> None:
        """Handling spaces in contact number during creation."""
        customer_with_spaces: CustomerBase = CustomerBase(
            name="Test Customer",
            email="test@example.com",
            contact_no=PhoneNumber("   +923001234567   "),
            address="Test Address",
        )

        result: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**customer_with_spaces.model_dump()),
        )

        assert " " not in result.contact_no
        assert (
            result.contact_no == str(customer_with_spaces.contact_no).strip()
        )

    def test_create_multiple_customers(self) -> None:
        """Creating multiple customers."""
        # Create multiple test customers
        result: Sequence[Customer] = self.customer_view.create_multiple(
            db_session=self.session,
            records=[
                Customer(**self.test_customer_1.model_dump()),
                Customer(**self.test_customer_2.model_dump()),
            ],
        )

        # Verify customers are created
        assert len(result) == 2
        assert all(c.id is not None for c in result)
        assert all(c.created_at is not None for c in result)
        assert all(c.updated_at is None for c in result)
        assert all(
            c.model_dump(exclude={"id", "created_at", "updated_at"})
            in [
                self.test_customer_1.model_dump(),
                self.test_customer_2.model_dump(),
            ]
            for c in result
        )

    def test_read_customer_by_id(self) -> None:
        """Retrieving a customer by ID."""
        customer: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        result: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=customer.id
        )

        assert result is not None
        assert customer.model_dump() == result.model_dump()

    def test_read_non_existent_customer(self) -> None:
        """Retrieving a non-existent customer."""
        non_existent_id: int = -1
        result: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_read_multiple_customers_by_ids(self) -> None:
        """Retrieving multiple customers by ID."""
        # Create multiple test customers
        result: Sequence[Customer] = self.customer_view.create_multiple(
            db_session=self.session,
            records=[
                Customer(**self.test_customer_1.model_dump()),
                Customer(**self.test_customer_2.model_dump()),
            ],
        )

        # Retrieve multiple customers by ID
        retrieved_customers: Sequence[Customer] = (
            self.customer_view.read_multiple_by_ids(
                db_session=self.session, record_ids=[c.id for c in result]
            )
        )

        assert len(retrieved_customers) == len(result)
        assert all(
            rc.model_dump() == c.model_dump()
            for rc, c in zip(retrieved_customers, result, strict=False)
        )

    def test_read_all_customers(self) -> None:
        """Retrieving all customers."""
        # Create multiple test customers
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )

        result: PaginationBase[Customer] = self.customer_view.read_all(
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
            c.email == self.test_customer_1.email for c in result.records
        )
        assert any(
            c.email == self.test_customer_2.email for c in result.records
        )

    def test_read_all_customers_pagination(self) -> None:
        """Customer pagination with multiple pages."""
        # Create three test customers to test pagination
        customer_1: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )
        customer_2: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )
        customer_3: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_3.model_dump()),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[Customer] = self.customer_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        # Assert first page
        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == customer_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert any(c.email == customer_1.email for c in page1_result.records)
        assert any(c.email == customer_2.email for c in page1_result.records)
        assert all(c.email != customer_3.email for c in page1_result.records)

        # Test second page
        page2_result: PaginationBase[Customer] = self.customer_view.read_all(
            db_session=self.session, page=2, limit=2
        )

        # Assert second page
        assert page2_result.current_page == 2
        assert page2_result.limit == 2
        assert page2_result.total_pages == 2
        assert page2_result.total_records == 3
        assert page2_result.next_record_id is None
        assert page2_result.previous_record_id == 1
        assert len(page2_result.records) == 1
        assert any(c.email == customer_3.email for c in page2_result.records)
        assert all(c.email != customer_1.email for c in page2_result.records)
        assert all(c.email != customer_2.email for c in page2_result.records)

    def test_search_customer_by_email(self) -> None:
        """Searching customers by email."""
        # Create test customers
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_3.model_dump()),
        )

        # Search for customers with specific domain
        result: PaginationBase[Customer] = self.customer_view.read_all(
            db_session=self.session,
            search_by="email",
            search_query="@example.com",
        )

        assert result.total_records == 2
        assert all("@example.com" in str(c.email) for c in result.records)

    def test_search_customer_by_invalid_column(self) -> None:
        """Search customer by invalid column name."""
        # Create test customers
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )
        self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_3.model_dump()),
        )

        with pytest.raises(ValueError) as exc_info:
            self.customer_view.read_all(
                db_session=self.session,
                search_by="invalid",
                search_query="@example.com",
            )

        assert "Invalid search column" in str(exc_info.value)

    def test_update_customer(self) -> None:
        """Updating a customer."""
        customer: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        result: Customer | None = self.customer_view.update_by_id(
            db_session=self.session,
            record_id=customer.id,
            record=Customer(**self.test_customer_2.model_dump()),
        )

        assert result is not None
        assert result.id == customer.id
        assert result.model_dump() == customer.model_dump()

    def test_update_non_existent_customer(self) -> None:
        """Updating a non-existent customer."""
        non_existent_id: int = -1
        result: Customer | None = self.customer_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        assert result is None

    def test_update_duplicate_email_validation(self) -> None:
        """Validating duplicate email during update."""
        # Create first customer
        customer_1: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        # Create second customer
        customer_2: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )

        # Update second customer with email of first customer
        customer_2.email = customer_1.email

        with pytest.raises(IntegrityError) as exc_info:
            self.customer_view.update_by_id(
                db_session=self.session,
                record_id=customer_2.id,
                record=customer_2,
            )

        assert "UNIQUE constraint failed: customer.email" in str(
            exc_info.value
        )

    def test_update_duplicate_contact_no_validation(self) -> None:
        """Validating duplicate contact number during update."""
        # Create first customer
        customer_1: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        # Create second customer
        customer_2: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_2.model_dump()),
        )

        # Update second customer with contact number of first customer
        customer_2.contact_no = customer_1.contact_no

        with pytest.raises(IntegrityError) as exc_info:
            self.customer_view.update_by_id(
                db_session=self.session,
                record_id=customer_2.id,
                record=customer_2,
            )

        assert "UNIQUE constraint failed: customer.contact_no" in str(
            exc_info.value
        )

    def test_update_multiple_customers_by_ids(self) -> None:
        """Updating multiple customers."""
        # Create multiple test customers
        customers: Sequence[Customer] = self.customer_view.create_multiple(
            db_session=self.session,
            records=[
                Customer(**self.test_customer_1.model_dump()),
                Customer(**self.test_customer_2.model_dump()),
            ],
        )

        customer_1: CustomerBase = CustomerBase(
            name="Updated Test Customer 1",
            email="updatedtest1@example.com",
            contact_no=PhoneNumber("+923031234567"),
            address="Updated Test Address 1",
        )
        customer_2: CustomerBase = CustomerBase(
            name="Updated Test Customer 2",
            email="updatedtest2@example.com",
            contact_no=PhoneNumber("+923041234567"),
            address="Updated Test Address 2",
        )

        # Update multiple customers
        updated_customers: Sequence[Customer] = (
            self.customer_view.update_multiple_by_ids(
                db_session=self.session,
                record_ids=[c.id for c in customers],
                records=[
                    Customer(**customer_1.model_dump()),
                    Customer(**customer_2.model_dump()),
                ],
            )
        )

        # Verify customers are updated
        assert len(updated_customers) == 2
        assert all(c.id is not None for c in updated_customers)
        assert all(c.created_at is not None for c in updated_customers)
        assert all(c.updated_at is not None for c in updated_customers)
        assert all(
            c.model_dump(exclude={"id", "created_at", "updated_at"})
            in [customer_1.model_dump(), customer_2.model_dump()]
            for c in updated_customers
        )

    def test_delete_customer(self) -> None:
        """Deleting a customer."""
        customer: Customer = self.customer_view.create(
            db_session=self.session,
            record=Customer(**self.test_customer_1.model_dump()),
        )

        result: Message | None = self.customer_view.delete_by_id(
            db_session=self.session, record_id=customer.id
        )

        assert result is not None
        assert result == Message(message="Record deleted successfully")

        # Verify customer no longer exists
        retrieved_customer: Customer | None = self.customer_view.read_by_id(
            db_session=self.session, record_id=customer.id
        )

        assert retrieved_customer is None

    def test_delete_non_existent_customer(self) -> None:
        """Deleting a non-existent customer."""
        non_existent_id: int = -1
        result: Message | None = self.customer_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_delete_multiple_customers_by_ids(self) -> None:
        """Deleting multiple customers."""
        # Create multiple test customers
        customers: Sequence[Customer] = self.customer_view.create_multiple(
            db_session=self.session,
            records=[
                Customer(**self.test_customer_1.model_dump()),
                Customer(**self.test_customer_2.model_dump()),
            ],
        )

        result: Message | None = self.customer_view.delete_multiple_by_ids(
            db_session=self.session, record_ids=[c.id for c in customers]
        )

        assert result is not None
        assert result == Message(message="Records deleted successfully")

        # Verify customers no longer exist
        retrieved_customers: Sequence[Customer] = (
            self.customer_view.read_multiple_by_ids(
                db_session=self.session, record_ids=[c.id for c in customers]
            )
        )

        assert len(retrieved_customers) == 0
