"""Supplier Test Cases.

Description:
- This file contains test cases for supplier operations.

"""

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.exc import IntegrityError

from tests.conftest import TestSetup
from workshop_management_system.v1.base.model import PaginationBase
from workshop_management_system.v1.supplier.model import Supplier, SupplierBase
from workshop_management_system.v1.supplier.view import SupplierView


class TestSupplier(TestSetup):
    """Test cases for supplier operations.

    Description:
    - This class provides test cases for supplier operations.

    Attributes:
    - `supplier_view` (SupplierView): An instance of SupplierView class.
    - `test_supplier_1` (SupplierBase): An instance of SupplierBase class for
    validation.
    - `test_supplier_2` (SupplierBase): An instance of SupplierBase class for
    validation.

    """

    supplier_view: SupplierView
    test_supplier_1: SupplierBase
    test_supplier_2: SupplierBase
    test_supplier_3: SupplierBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.supplier_view = SupplierView(Supplier)
        self.test_supplier_1 = SupplierBase(
            name="Test Supplier 1",
            email="test1@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address 1",
        )
        self.test_supplier_2 = SupplierBase(
            name="Test Supplier 2",
            email="test2@example.com",
            contact_no=PhoneNumber("+923011234567"),
            address="Test Address 2",
        )
        self.test_supplier_3 = SupplierBase(
            name="Test Supplier 3",
            email="test3@example.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address 3",
        )

    def test_create_supplier(self) -> None:
        """Creating a supplier."""
        result: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == self.test_supplier_1.model_dump()
        )

    def test_duplicate_email_validation(self) -> None:
        """Validating duplicate email."""
        # Create first supplier
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        # Create second supplier with same email but different phone
        duplicate_email_supplier: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test1@example.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.supplier_view.create(
                db_session=self.session,
                record=Supplier(**duplicate_email_supplier.model_dump()),
            )

        assert "UNIQUE constraint failed: supplier.email" in str(
            exc_info.value
        )

    def test_invalid_email_validation(self) -> None:
        """Validating invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            SupplierBase(
                name="Test Supplier",
                email="invalid.email@",
                contact_no=PhoneNumber("+923021234567"),
                address="Test Address",
            )

        assert "value is not a valid email address" in str(exc_info.value)

    def test_email_spaces_handling(self) -> None:
        """Handling spaces in email during creation."""
        supplier_with_spaces: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="   test.spaces@example.com   ",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address",
        )

        result: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**supplier_with_spaces.model_dump()),
        )

        if result.email and supplier_with_spaces.email:
            assert " " not in str(result.email)
            assert str(result.email) == str(supplier_with_spaces.email).strip()
        assert (
            result.model_dump(exclude={"id", "created_at", "updated_at"})
            == supplier_with_spaces.model_dump()
        )

    def test_duplicate_contact_no_validation(self) -> None:
        """Validating duplicate contact number."""
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        # Create second supplier with same contact number but different email
        duplicate_contact_no_supplier: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.supplier_view.create(
                db_session=self.session,
                record=Supplier(**duplicate_contact_no_supplier.model_dump()),
            )

        assert "UNIQUE constraint failed: supplier.contact_no" in str(
            exc_info.value
        )

    def test_invalid_contact_no_validation(self) -> None:
        """Validating invalid contact number format."""
        with pytest.raises(ValidationError) as exc_info:
            SupplierBase(
                name="Test Supplier",
                email="test@example.com",
                contact_no=PhoneNumber("1234567890"),
                address="Test Address",
            )

        assert "value is not a valid phone number" in str(exc_info.value)

        # Test with wrong country code
        with pytest.raises(ValidationError) as exc_info:
            SupplierBase(
                name="Test Supplier",
                email="test@example.com",
                contact_no=PhoneNumber("+123001234567"),
                address="Test Address",
            )

        assert "value is not a valid phone number" in str(exc_info.value)

    def test_contact_no_spaces_handling(self) -> None:
        """Handling spaces in contact number during creation."""
        supplier_with_spaces: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test@example.com",
            contact_no=PhoneNumber("   +923001234567   "),
            address="Test Address",
        )

        result: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**supplier_with_spaces.model_dump()),
        )

        assert " " not in result.contact_no
        assert (
            result.contact_no == str(supplier_with_spaces.contact_no).strip()
        )

    def test_read_supplier_by_id(self) -> None:
        """Retrieving a supplier by ID."""
        supplier: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        result: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=supplier.id
        )

        assert result is not None
        assert supplier.model_dump() == result.model_dump()

    def test_read_non_existent_supplier(self) -> None:
        """Retrieving a non-existent supplier."""
        non_existent_id: int = -1
        result: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_read_all_suppliers(self) -> None:
        """Retrieving all suppliers."""
        # Create multiple test suppliers
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_2.model_dump()),
        )

        result: PaginationBase[Supplier] = self.supplier_view.read_all(
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
            s.email == self.test_supplier_1.email for s in result.records
        )
        assert any(
            s.email == self.test_supplier_2.email for s in result.records
        )

    def test_read_all_suppliers_pagination(self) -> None:
        """Supplier pagination with multiple pages."""
        # Create three test suppliers to test pagination
        supplier_1: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )
        supplier_2: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_2.model_dump()),
        )
        supplier_3: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_3.model_dump()),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[Supplier] = self.supplier_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        # Assert first page
        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == supplier_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert any(s.email == supplier_1.email for s in page1_result.records)
        assert any(s.email == supplier_2.email for s in page1_result.records)
        assert all(s.email != supplier_3.email for s in page1_result.records)

        # Test second page
        page2_result: PaginationBase[Supplier] = self.supplier_view.read_all(
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
        assert any(s.email == supplier_3.email for s in page2_result.records)
        assert all(s.email != supplier_1.email for s in page2_result.records)
        assert all(s.email != supplier_2.email for s in page2_result.records)

    def test_update_supplier(self) -> None:
        """Updating a supplier."""
        supplier: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        result: Supplier | None = self.supplier_view.update_by_id(
            db_session=self.session,
            record_id=supplier.id,
            record=Supplier(**self.test_supplier_2.model_dump()),
        )

        assert result is not None
        assert result.id == supplier.id
        assert result.model_dump() == supplier.model_dump()

    def test_update_non_existent_supplier(self) -> None:
        """Updating a non-existent supplier."""
        non_existent_id: int = -1
        result: Supplier | None = self.supplier_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        assert result is None

    def test_update_duplicate_email_validation(self) -> None:
        """Validating duplicate email during update."""
        # Create first supplier
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        # Create second supplier
        supplier: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_2.model_dump()),
        )

        # Update second supplier with email of first supplier
        duplicate_email_supplier: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test1@example.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.supplier_view.update_by_id(
                db_session=self.session,
                record_id=supplier.id,
                record=Supplier(**duplicate_email_supplier.model_dump()),
            )

        assert "UNIQUE constraint failed: supplier.email" in str(
            exc_info.value
        )

    def test_update_duplicate_contact_no_validation(self) -> None:
        """Validating duplicate contact number during update."""
        self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        # Create second supplier
        supplier: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_2.model_dump()),
        )

        # Update second supplier with contact number of first supplier
        duplicate_contact_no_supplier: SupplierBase = SupplierBase(
            name="Test Supplier",
            email="test@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address",
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.supplier_view.update_by_id(
                db_session=self.session,
                record_id=supplier.id,
                record=Supplier(**duplicate_contact_no_supplier.model_dump()),
            )

        assert "UNIQUE constraint failed: supplier.contact_no" in str(
            exc_info.value
        )

    def test_delete_supplier(self) -> None:
        """Deleting a supplier."""
        supplier: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**self.test_supplier_1.model_dump()),
        )

        result: Supplier | None = self.supplier_view.delete_by_id(
            db_session=self.session, record_id=supplier.id
        )

        assert result is not None
        assert result.id == supplier.id

        # Verify supplier no longer exists
        retrieved_supplier: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=supplier.id
        )

        assert retrieved_supplier is None

    def test_delete_non_existent_supplier(self) -> None:
        """Deleting a non-existent supplier."""
        non_existent_id: int = -1
        result: Supplier | None = self.supplier_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None
