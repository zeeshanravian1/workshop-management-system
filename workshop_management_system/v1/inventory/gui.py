import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView


# Embedded: Dialog for adding a new inventory item.
class InventoryDialog(QDialog):
    """Dialog to add a new inventory item."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add New Inventory")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.item_name_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.unit_price_input = QLineEdit()
        self.minimum_threshold_input = QLineEdit()
        self.category_dropdown = QComboBox()
        # Add category options.
        self.category_dropdown.addItem("Maintenance")
        self.category_dropdown.addItem("Spare Parts")
        self.category_dropdown.addItem("Others")
        layout.addRow("Item Name:", self.item_name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Unit Price:", self.unit_price_input)
        layout.addRow("Minimum Threshold:", self.minimum_threshold_input)
        layout.addRow("Category:", self.category_dropdown)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        return {
            "item_name": self.item_name_input.text().strip(),
            "quantity": int(self.quantity_input.text().strip() or 0),
            "unit_price": float(self.unit_price_input.text().strip() or 0),
            "minimum_threshold": int(
                self.minimum_threshold_input.text().strip() or 0
            ),
            "category": self.category_dropdown.currentText(),
        }


# Embedded: Dialog for updating an existing inventory item.
class InventoryUpdateDialog(QDialog):
    """Dialog to update an existing inventory item."""

    def __init__(self, initial_data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Update Inventory")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.item_name_input = QLineEdit(initial_data.get("Item Name", ""))
        self.quantity_input = QLineEdit(str(initial_data.get("Quantity", "")))
        self.unit_price_input = QLineEdit(
            str(initial_data.get("Unit Price", ""))
        )
        self.minimum_threshold_input = QLineEdit(
            str(initial_data.get("Minimum Threshold", ""))
        )
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItem("Maintenance")
        self.category_dropdown.addItem("Spare Parts")
        self.category_dropdown.addItem("Others")
        # Set current category if available.
        current_category = initial_data.get("Category", "Others")
        index = self.category_dropdown.findText(current_category)
        if index != -1:
            self.category_dropdown.setCurrentIndex(index)
        layout.addRow("Item Name:", self.item_name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Unit Price:", self.unit_price_input)
        layout.addRow("Minimum Threshold:", self.minimum_threshold_input)
        layout.addRow("Category:", self.category_dropdown)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        return {
            "item_name": self.item_name_input.text().strip(),
            "quantity": int(self.quantity_input.text().strip() or 0),
            "unit_price": float(self.unit_price_input.text().strip() or 0),
            "minimum_threshold": int(
                self.minimum_threshold_input.text().strip() or 0
            ),
            "category": self.category_dropdown.currentText(),
        }


class InventoryGUI(BaseGUI):
    """Inventory GUI Class."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # Insert header label with designated object name
        header = QLabel(
            "Inventory Management", alignment=Qt.AlignmentFlag.AlignCenter
        )
        header.setObjectName("headerLabel")
        self.layout().insertWidget(0, header)

        self.inventory_view = InventoryView(Inventory)
        self.all_items = self.load_inventories()
        self.filtered_items = self.all_items.copy()
        self.load_items()

    def get_search_criteria(self) -> list[str]:
        return [
            "ID",
            "Item Name",
            "Quantity",
            "Unit Price",
            "Minimum Threshold",
            "Category",
        ]

    def load_inventories(self) -> list[dict]:
        # Placeholder inventory data based on inventory/model.py fields
        return [
            {
                "ID": 1,
                "Item Name": "Engine Oil",
                "Quantity": 50,
                "Unit Price": 25.0,
                "Minimum Threshold": 10,
                "Category": "Maintenance",
            },
            {
                "ID": 2,
                "Item Name": "Brake Pads",
                "Quantity": 30,
                "Unit Price": 40.0,
                "Minimum Threshold": 5,
                "Category": "Spare Parts",
            },
        ]

    def load_items(self) -> None:
        # Overriding to setup inventory-specific columns
        self.customer_table.setRowCount(
            len(self.filtered_items) + 1
        )  # +1 for header
        self.customer_table.setColumnCount(6)
        headers = [
            "ID",
            "Item Name",
            "Quantity",
            "Unit Price",
            "Minimum Threshold",
            "Category",
        ]
        for col, hdr in enumerate(headers):
            item = QTableWidgetItem(hdr)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)
        for row, data in enumerate(self.filtered_items, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(data["ID"]))
            )
            self.customer_table.setItem(
                row, 1, QTableWidgetItem(data["Item Name"])
            )
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(str(data["Quantity"]))
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(str(data["Unit Price"]))
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(str(data["Minimum Threshold"]))
            )
            self.customer_table.setItem(
                row, 5, QTableWidgetItem(data["Category"])
            )

    def add_inventory(self) -> None:
        """Open dialog to add a new inventory item."""
        dialog = InventoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            # Normally, add the new Inventory to the DB.
            QMessageBox.information(
                self,
                "Inventory Data",
                f"Item Name: {data['item_name']}\nQuantity: {data['quantity']}\n"
                f"Unit Price: {data['unit_price']}\nMinimum Threshold: {data['minimum_threshold']}\n"
                f"Category: {data['category']}",
            )

    def update_inventory(self) -> None:
        """Open dialog to update the selected inventory item."""
        selected_row = self.customer_table.currentRow()
        if selected_row < 1:
            QMessageBox.warning(
                self, "Update", "Please select an inventory item to update."
            )
            return
        current_data = {
            "Item Name": self.customer_table.item(selected_row, 1).text(),
            "Quantity": int(self.customer_table.item(selected_row, 2).text()),
            "Unit Price": float(
                self.customer_table.item(selected_row, 3).text()
            ),
            "Minimum Threshold": int(
                self.customer_table.item(selected_row, 4).text()
            ),
            "Category": self.customer_table.item(selected_row, 5).text(),
        }
        dialog = InventoryUpdateDialog(initial_data=current_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            # Normally, update the Inventory record in the DB.
            QMessageBox.information(
                self,
                "Updated Inventory Data",
                f"Item Name: {updated_data['item_name']}\nQuantity: {updated_data['quantity']}\n"
                f"Unit Price: {updated_data['unit_price']}\nMinimum Threshold: {updated_data['minimum_threshold']}\n"
                f"Category: {updated_data['category']}",
            )

    def delete_inventory(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Delete", "Delete inventory functionality"
            )

    def show_context_menu(self, position) -> None:
        row = self.customer_table.rowAt(position.y())
        if row >= 0:
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            self.apply_styles(context_menu)
            update_action = context_menu.addAction("✏️  Update")
            update_action.setStatusTip("Update selected inventory")
            context_menu.addSeparator()
            delete_action = context_menu.addAction("🗑️  Delete")
            delete_action.setStatusTip("Delete selected inventory")
            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_inventory()
            elif action == delete_action:
                self.delete_inventory()

    def add(self) -> None:
        """Override base add method to open the add inventory dialog."""
        self.add_inventory()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    inventory_gui = InventoryGUI(main_window)
    main_window.setCentralWidget(inventory_gui)
    main_window.setWindowTitle("Inventory Management System")
    main_window.resize(800, 600)
    inventory_gui.apply_styles(main_window)
    inventory_gui.apply_styles()
    main_window.show()
    sys.exit(app.exec())
