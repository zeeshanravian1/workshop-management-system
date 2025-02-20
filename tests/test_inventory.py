"""Inventory Test Cases.

Description:
- This file contains test cases for inventory operations.

"""

import pytest
from pydantic import ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.exc import IntegrityError

from tests.conftest import TestSetup
from workshop_management_system.core.config import InventoryCategory
from workshop_management_system.v1.base.model import PaginationBase
from workshop_management_system.v1.inventory.model import (
    Inventory,
    InventoryBase,
)
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.supplier.model import Supplier, SupplierBase
from workshop_management_system.v1.supplier.view import SupplierView


class TestInventory(TestSetup):
    """Test cases for inventory operations.

    Description:
    - This class provides test cases for inventory operations.

    Attributes:
    - `supplier_view` (SupplierView): An instance of SupplierView class.
    - `test_supplier_1` (SupplierBase): An instance of SupplierBase class for
    validation.
    - `test_supplier_2` (SupplierBase): An instance of SupplierBase class for
    validation.
    - `inventory_view` (InventoryView): An instance of InventoryView class.
    - `test_inventory_1` (InventoryBase): An instance of InventoryBase class
    for validation.
    - `test_inventory_2` (InventoryBase): An instance of InventoryBase class
    for validation.

    """

    supplier_view: SupplierView
    test_supplier_1: Supplier
    test_supplier_2: Supplier
    test_supplier_3: Supplier
    inventory_view: InventoryView
    test_inventory_1: InventoryBase
    test_inventory_2: InventoryBase
    test_inventory_3: InventoryBase

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Setup method for test cases."""
        self.supplier_view = SupplierView(Supplier)
        self.inventory_view = InventoryView(Inventory)

        # Create suppliers instances for validation
        supplier_1 = SupplierBase(
            name="Test Supplier 1",
            email="test1@example.com",
            contact_no=PhoneNumber("+923001234567"),
            address="Test Address 1",
        )
        supplier_2 = SupplierBase(
            name="Test Supplier 2",
            email="test2@example.com",
            contact_no=PhoneNumber("+923011234567"),
            address="Test Address 2",
        )
        supplier_3 = SupplierBase(
            name="Test Supplier 3",
            email="test3@example.com",
            contact_no=PhoneNumber("+923021234567"),
            address="Test Address 3",
        )

        # Create suppliers
        self.test_supplier_1: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**supplier_1.model_dump()),
        )
        self.test_supplier_2: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**supplier_2.model_dump()),
        )
        self.test_supplier_3: Supplier = self.supplier_view.create(
            db_session=self.session,
            record=Supplier(**supplier_3.model_dump()),
        )

        # Setup test inventory items
        self.test_inventory_1 = InventoryBase(
            item_name="Test Item 1",
            quantity=100,
            unit_price=10.5,
            minimum_threshold=20,
            category=InventoryCategory.LUBRICANTS,
        )
        self.test_inventory_2 = InventoryBase(
            item_name="Test Item 2",
            quantity=50,
            unit_price=15.75,
            minimum_threshold=10,
            category=InventoryCategory.SPARE_PARTS,
        )
        self.test_inventory_3 = InventoryBase(
            item_name="Test Item 3",
            quantity=75,
            unit_price=20.0,
            minimum_threshold=15,
            category=InventoryCategory.TOOLS,
        )

    def test_duplicate_item_name_validation(self) -> None:
        """Validating duplicate item name."""
        # Create first inventory item
        self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Create second inventory item with same item name
        duplicate_item_name_inventory: InventoryBase = InventoryBase(
            item_name="Test Item 1",
            quantity=200,
            unit_price=20.5,
            minimum_threshold=30,
            category=InventoryCategory.LUBRICANTS,
        )

        with pytest.raises(IntegrityError) as exc_info:
            self.inventory_view.create(
                db_session=self.session,
                record=Inventory(
                    **duplicate_item_name_inventory.model_dump(),
                    suppliers=[self.test_supplier_2],
                ),
            )

        assert "UNIQUE constraint failed: inventory.item_name" in str(
            exc_info.value
        )

    def test_quantity_gt_zero_validation(self) -> None:
        """Validating quantity greater than zero."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryBase(
                item_name="Test Item",
                quantity=0,
                unit_price=10.5,
                minimum_threshold=20,
                category=InventoryCategory.LUBRICANTS,
            )

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_unit_price_gt_zero_validation(self) -> None:
        """Validating unit price greater than zero."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryBase(
                item_name="Test Item",
                quantity=100,
                unit_price=0,
                minimum_threshold=20,
                category=InventoryCategory.LUBRICANTS,
            )

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_minimum_threshold_gt_zero_validation(self) -> None:
        """Validating minimum threshold greater than zero."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryBase(
                item_name="Test Item",
                quantity=100,
                unit_price=10.5,
                minimum_threshold=0,
                category=InventoryCategory.LUBRICANTS,
            )

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_category_validation(self) -> None:
        """Validating category."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryBase(
                item_name="Test Item",
                quantity=100,
                unit_price=10.5,
                minimum_threshold=20,
                category="Invalid Category",  # type: ignore
            )

        categories: list[str] = [f"'{key.value}'" for key in InventoryCategory]
        validation: str = (
            " or ".join([", ".join(categories[:-1]), categories[-1]])
            if len(categories) > 1
            else categories[0]
        )

        assert f"Input should be {validation}" in str(exc_info.value)

    def test_create_inventory_with_single_supplier(self) -> None:
        """Creating an inventory item with a single supplier."""
        # Create inventory item
        result: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "suppliers"}
            )
            == self.test_inventory_1.model_dump()
        )
        assert len(result.suppliers) == 1
        assert result.suppliers[0] == self.test_supplier_1

    def test_create_inventory_with_multiple_suppliers(self) -> None:
        """Creating an inventory item with multiple suppliers."""
        # Create inventory item
        result: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1, self.test_supplier_2],
            ),
        )

        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is None
        assert (
            result.model_dump(
                exclude={"id", "created_at", "updated_at", "suppliers"}
            )
            == self.test_inventory_1.model_dump()
        )
        assert len(result.suppliers) == 2
        assert self.test_supplier_1 in result.suppliers
        assert self.test_supplier_2 in result.suppliers

    def test_read_inventory_by_id_with_single_supplier(self) -> None:
        """Retrieving an inventory with a single supplier."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        result: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert result is not None
        assert inventory.model_dump() == result.model_dump()
        assert len(result.suppliers) == 1
        assert result.suppliers[0] == self.test_supplier_1

    def test_read_inventory_by_id_with_multiple_suppliers(self) -> None:
        """Retrieving an inventory with multiple suppliers."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1, self.test_supplier_2],
            ),
        )

        result: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert result is not None
        assert inventory.model_dump() == result.model_dump()
        assert len(result.suppliers) == 2
        assert self.test_supplier_1 in result.suppliers
        assert self.test_supplier_2 in result.suppliers

    def test_read_non_existent_inventory(self) -> None:
        """Retrieving a non-existent inventory."""
        non_existent_id: int = -1
        result: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_read_all_inventories(self) -> None:
        """Retrieving all inventories."""
        # Create multiple test inventories
        self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )
        self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_2.model_dump(),
                suppliers=[self.test_supplier_2],
            ),
        )

        result: PaginationBase[Inventory] = self.inventory_view.read_all(
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
            i.item_name == self.test_inventory_1.item_name
            for i in result.records
        )
        assert any(
            i.item_name == self.test_inventory_2.item_name
            for i in result.records
        )

    def test_read_all_inventories_pagination(self) -> None:
        """Inventory pagination with multiple pages."""
        # Create three test inventories to test pagination
        inventory_1: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )
        inventory_2: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_2.model_dump(),
                suppliers=[self.test_supplier_2],
            ),
        )
        inventory_3: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_3.model_dump(),
                suppliers=[self.test_supplier_1, self.test_supplier_2],
            ),
        )

        # Test first page with limit of 2
        page1_result: PaginationBase[Inventory] = self.inventory_view.read_all(
            db_session=self.session, page=1, limit=2
        )

        # Assert first page
        assert page1_result.current_page == 1
        assert page1_result.limit == 2
        assert page1_result.total_pages == 2
        assert page1_result.total_records == 3
        assert page1_result.next_record_id == inventory_2.id + 1
        assert page1_result.previous_record_id is None
        assert len(page1_result.records) == 2
        assert any(
            i.item_name == inventory_1.item_name for i in page1_result.records
        )
        assert any(
            i.item_name == inventory_2.item_name for i in page1_result.records
        )
        assert all(
            i.item_name != inventory_3.item_name for i in page1_result.records
        )

        # Test second page
        page2_result: PaginationBase[Inventory] = self.inventory_view.read_all(
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
        assert any(
            i.item_name == inventory_3.item_name for i in page2_result.records
        )
        assert all(
            i.item_name != inventory_1.item_name for i in page2_result.records
        )
        assert all(
            i.item_name != inventory_2.item_name for i in page2_result.records
        )

    def test_update_inventory(self) -> None:
        """Updating an inventory item."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        result: Inventory | None = self.inventory_view.update_by_id(
            db_session=self.session,
            record_id=inventory.id,
            record=Inventory(**self.test_inventory_2.model_dump()),
        )

        assert result is not None
        assert result.id == inventory.id
        assert result.model_dump() == inventory.model_dump()

    def test_update_non_existent_inventory(self) -> None:
        """Updating a non-existent inventory item."""
        non_existent_id: int = -1

        result: Inventory | None = self.inventory_view.update_by_id(
            db_session=self.session,
            record_id=non_existent_id,
            record=Inventory(**self.test_inventory_1.model_dump()),
        )

        assert result is None

    def test_update_duplicate_item_name_validation(self) -> None:
        """Validating duplicate item name during update."""
        # Create first inventory item
        inventory_1: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Create second inventory item
        inventory_2: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_2.model_dump(),
                suppliers=[self.test_supplier_2],
            ),
        )

        # Update second inventory item with item name of first inventory item
        inventory_2.item_name = inventory_1.item_name

        with pytest.raises(IntegrityError) as exc_info:
            self.inventory_view.update_by_id(
                db_session=self.session,
                record_id=inventory_2.id,
                record=inventory_2,
            )

        assert "UNIQUE constraint failed: inventory.item_name" in str(
            exc_info.value
        )

    def test_update_inventory_supplier_with_single_supplier(self) -> None:
        """Updating inventory supplier with single supplier."""
        # Create inventory item with initial supplier
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Update supplier
        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=inventory.id,
            previous_supplier_id=self.test_supplier_1.id,
            new_supplier_id=self.test_supplier_2.id,
        )

        assert result is not None
        assert result.id == inventory.id
        assert len(result.suppliers) == 1
        assert self.test_supplier_2 in result.suppliers
        assert self.test_supplier_1 not in result.suppliers

    def test_update_inventory_supplier_with_multiple_suppliers(self) -> None:
        """Updating inventory supplier with multiple suppliers."""
        # Create inventory item with initial suppliers
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1, self.test_supplier_2],
            ),
        )

        # Update supplier
        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=inventory.id,
            previous_supplier_id=self.test_supplier_1.id,
            new_supplier_id=self.test_supplier_3.id,
        )

        assert result is not None
        assert result.id == inventory.id
        assert len(result.suppliers) == 2
        assert self.test_supplier_2 in result.suppliers
        assert self.test_supplier_3 in result.suppliers
        assert self.test_supplier_1 not in result.suppliers

    def test_update_inventory_supplier_non_existent_inventory(self) -> None:
        """Updating supplier of non-existent inventory."""
        non_existent_id: int = -1

        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=non_existent_id,
            previous_supplier_id=self.test_supplier_1.id,
            new_supplier_id=self.test_supplier_2.id,
        )

        assert result is None

    def test_update_inventory_supplier_non_existent_previous_supplier(
        self,
    ) -> None:
        """Updating an inventory with non-existent previous supplier."""
        # Create inventory item with initial supplier
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        non_existent_supplier_id: int = -1

        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=inventory.id,
            previous_supplier_id=non_existent_supplier_id,
            new_supplier_id=self.test_supplier_2.id,
        )

        assert result is None

        # Verify original supplier relationship remains unchanged
        db_record: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )
        assert db_record is not None
        assert len(db_record.suppliers) == 1
        assert self.test_supplier_1 in db_record.suppliers

    def test_update_inventory_supplier_non_existent_new_supplier(self) -> None:
        """Updating with non-existent new supplier."""
        # Create inventory item with initial supplier
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        non_existent_supplier_id: int = -1

        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=inventory.id,
            previous_supplier_id=self.test_supplier_1.id,
            new_supplier_id=non_existent_supplier_id,
        )

        assert result is None

        # Verify original supplier relationship remains unchanged
        db_record: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )
        assert db_record is not None
        assert len(db_record.suppliers) == 1
        assert self.test_supplier_1 in db_record.suppliers

    def test_update_supplier_wrong_previous_supplier(self) -> None:
        """Updating with wrong previous supplier."""
        # Create inventory item with initial supplier
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Try to update with wrong previous supplier
        result: Inventory | None = self.inventory_view.update_supplier(
            db_session=self.session,
            record_id=inventory.id,
            previous_supplier_id=self.test_supplier_2.id,
            new_supplier_id=self.test_supplier_2.id,
        )

        assert result is None

        # Verify original supplier relationship remains unchanged
        db_record: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )
        assert db_record is not None
        assert len(db_record.suppliers) == 1
        assert self.test_supplier_1 in db_record.suppliers

    def test_delete_inventory_with_single_supplier(self) -> None:
        """Deleting an inventory item with a single supplier."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        result: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert result is not None
        assert result.id == inventory.id

        # Verify inventory no longer exists
        retrieved_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert retrieved_inventory is None

        # Verify supplier still exists
        supplier: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_1.id
        )

        assert supplier is not None
        assert supplier.id == self.test_supplier_1.id

    def test_delete_inventory_with_multiple_suppliers(self) -> None:
        """Deleting an inventory item with multiple suppliers."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1, self.test_supplier_2],
            ),
        )

        result: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert result is not None
        assert result.id == inventory.id

        # Verify inventory no longer exists
        retrieved_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert retrieved_inventory is None

        # Verify suppliers still exist
        supplier_1: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_1.id
        )
        supplier_2: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_2.id
        )

        assert supplier_1 is not None
        assert supplier_1.id == self.test_supplier_1.id
        assert supplier_2 is not None
        assert supplier_2.id == self.test_supplier_2.id

    def test_delete_non_existent_inventory(self) -> None:
        """Deleting a non-existent inventory item."""
        non_existent_id: int = -1

        result: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=non_existent_id
        )

        assert result is None

    def test_delete_multiple_inventories_with_shared_supplier(self) -> None:
        """Deleting multiple inventories with shared supplier."""
        # Create inventory items
        inventory_1: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )
        inventory_2: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_2.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Delete first inventory item
        result_1: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=inventory_1.id
        )

        assert result_1 is not None
        assert result_1.id == inventory_1.id

        # Verify first inventory no longer exists
        retrieved_inventory_1: Inventory | None = (
            self.inventory_view.read_by_id(
                db_session=self.session, record_id=inventory_1.id
            )
        )

        assert retrieved_inventory_1 is None

        # Verify second inventory still exists
        retrieved_inventory_2: Inventory | None = (
            self.inventory_view.read_by_id(
                db_session=self.session, record_id=inventory_2.id
            )
        )

        assert retrieved_inventory_2 is not None
        assert retrieved_inventory_2.id == inventory_2.id

        # Verify supplier still exists
        supplier: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_1.id
        )

        assert supplier is not None
        assert supplier.id == self.test_supplier_1.id

        # Delete second inventory item
        result_2: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=inventory_2.id
        )

        assert result_2 is not None
        assert result_2.id == inventory_2.id

        # Verify second inventory no longer exists
        retrieved_inventory2: Inventory | None = (
            self.inventory_view.read_by_id(
                db_session=self.session, record_id=inventory_2.id
            )
        )

        assert retrieved_inventory2 is None

        # Verify supplier still exists
        retrieved_supplier: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_1.id
        )

        assert retrieved_supplier is not None
        assert retrieved_supplier.id == self.test_supplier_1.id

    def test_delete_inventory_verify_supplier_links_deleted(self) -> None:
        """Verifying supplier links are deleted on inventory delete."""
        # Create inventory item
        inventory: Inventory = self.inventory_view.create(
            db_session=self.session,
            record=Inventory(
                **self.test_inventory_1.model_dump(),
                suppliers=[self.test_supplier_1],
            ),
        )

        # Delete inventory item
        result: Inventory | None = self.inventory_view.delete_by_id(
            db_session=self.session, record_id=inventory.id
        )

        assert result is not None
        assert result.id == inventory.id

        # Verify inventory no longer exists
        retrieved_inventory: Inventory | None = self.inventory_view.read_by_id(
            db_session=self.session,
            record_id=inventory.id,
        )

        assert retrieved_inventory is None

        # Verify supplier no longer linked to inventory
        supplier: Supplier | None = self.supplier_view.read_by_id(
            db_session=self.session, record_id=self.test_supplier_1.id
        )

        assert supplier is not None
        assert supplier.id == self.test_supplier_1.id
        assert len(supplier.inventories) == 0
