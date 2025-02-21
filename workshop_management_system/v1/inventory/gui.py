import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView


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
        QMessageBox.information(self, "Add", "Add inventory functionality")

    def update_inventory(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Update", "Update inventory functionality"
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
