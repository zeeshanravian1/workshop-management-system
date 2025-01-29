"""Inventory GUI Module.

Description:
- This module provides the GUI for managing inventory.

"""

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView


class InventoryGUI(QMainWindow):
    """Inventory GUI Class.

    Description:
    - This class provides the GUI for managing inventory.

    """

    def __init__(self):
        """Initialize the Inventory GUI."""
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setGeometry(100, 100, 800, 600)

        self.inventory_view = InventoryView(
            model=Inventory
        )  # Initialize InventoryView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setSelectionBehavior(
            self.inventory_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.inventory_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Inventory")
        self.load_button.clicked.connect(self.load_inventory)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Item")
        self.update_button.clicked.connect(self.update_item)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Item")
        self.delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_inventory()  # Load inventory on initialization

    def load_inventory(self):
        """Load inventory from the database and display them in the table."""
        try:
            with Session(engine) as session:
                inventory_items = self.inventory_view.read_all(
                    db_session=session
                )
                self.inventory_table.setRowCount(len(inventory_items))
                self.inventory_table.setColumnCount(5)
                self.inventory_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Item Name",
                        "Quantity",
                        "Unit Price",
                        "Minimum Stock Level",
                    ]
                )

                for row, item in enumerate(inventory_items):
                    self.inventory_table.setItem(
                        row, 0, QTableWidgetItem(str(item.id))
                    )
                    self.inventory_table.setItem(
                        row, 1, QTableWidgetItem(item.item_name)
                    )
                    self.inventory_table.setItem(
                        row, 2, QTableWidgetItem(str(item.quantity))
                    )
                    self.inventory_table.setItem(
                        row, 3, QTableWidgetItem(str(item.unit_price))
                    )
                    self.inventory_table.setItem(
                        row, 4, QTableWidgetItem(str(item.minimum_stock_level))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load inventory: {e!s}"
            )

    def add_item(self):
        """Add a new item to the inventory."""
        try:
            # Get item details from user
            item_name, ok = QInputDialog.getText(
                self, "Add Item", "Enter Item Name:"
            )
            if not ok or not item_name:
                return

            quantity, ok = QInputDialog.getInt(
                self, "Add Item", "Enter Quantity:"
            )
            if not ok:
                return

            unit_price, ok = QInputDialog.getDouble(
                self, "Add Item", "Enter Unit Price:"
            )
            if not ok:
                return

            min_stock, ok = QInputDialog.getInt(
                self, "Add Item", "Enter Minimum Stock Level:"
            )
            if not ok:
                return

            supplier_id, ok = QInputDialog.getInt(
                self, "Add Item", "Enter Supplier ID:"
            )
            if not ok:
                return

            with Session(engine) as session:
                new_item = Inventory(
                    # id will be auto-generated by the database
                    item_name=item_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    minimum_stock_level=min_stock,
                    supplier_id=supplier_id,
                )
                self.inventory_view.create(db_session=session, record=new_item)
                QMessageBox.information(
                    self, "Success", "Item added successfully!"
                )
                self.load_inventory()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {e!s}")

    def update_item(self):
        """Update an existing item."""
        try:
            selected_row = self.inventory_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an item to update."
                )
                return

            item = self.inventory_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected item ID is invalid."
                )
                return
            item_id = int(item.text())

            # Get updated details from user
            item_name, ok = QInputDialog.getText(
                self, "Update Item", "Enter New Item Name:"
            )
            if not ok or not item_name:
                return

            quantity, ok = QInputDialog.getInt(
                self, "Update Item", "Enter New Quantity:"
            )
            if not ok:
                return

            unit_price, ok = QInputDialog.getDouble(
                self, "Update Item", "Enter New Unit Price:"
            )
            if not ok:
                return

            min_stock, ok = QInputDialog.getInt(
                self, "Update Item", "Enter New Minimum Stock Level:"
            )
            if not ok:
                return

            with Session(engine) as session:
                item_obj = self.inventory_view.read_by_id(
                    db_session=session, record_id=item_id
                )
                if item_obj:
                    item_obj.item_name = item_name
                    item_obj.quantity = quantity
                    item_obj.unit_price = unit_price
                    item_obj.minimum_stock_level = min_stock
                    self.inventory_view.update(
                        db_session=session,
                        record_id=item_id,
                        record=item_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Item updated successfully!"
                    )
                    self.load_inventory()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update item: {e!s}"
            )

    def delete_item(self):
        """Delete an item from the inventory."""
        try:
            selected_row = self.inventory_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an item to delete."
                )
                return

            item = self.inventory_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected item ID is invalid."
                )
                return
            item_id = int(item.text())

            confirmation = QMessageBox.question(
                self,
                "Delete Item",
                "Are you sure you want to delete this item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.inventory_view.delete(
                        db_session=session, record_id=item_id
                    )
                    QMessageBox.information(
                        self, "Success", "Item deleted successfully!"
                    )
                    self.load_inventory()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete item: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = InventoryGUI()
    window.show()
    app.exec()
