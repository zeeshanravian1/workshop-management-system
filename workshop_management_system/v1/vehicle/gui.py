"""Vehicle GUI Module.

Description:
- This module provides the GUI components for the vehicle model.

"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView


class VehicleGUI(BaseGUI):
    """Vehicle GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Vehicle GUI."""
        super().__init__(parent)
        self.vehicle_view = VehicleView(Vehicle)
        self.all_items = self.load_vehicles()
        self.filtered_items = self.all_items.copy()
        self.load_items()

    def get_search_criteria(self) -> list[str]:
        """Get search criteria for vehicle model."""
        return ["ID", "Make", "Model", "Year", "Vehicle Number"]

    def load_vehicles(self) -> list[dict]:
        """Load vehicles from the database."""
        # Implement the logic to load vehicles from the database
        # This is a placeholder implementation
        return [
            {
                "ID": 1,
                "Make": "Toyota",
                "Model": "Corolla",
                "Year": 2020,
                "Vehicle Number": "ABC123",
            },
            {
                "ID": 2,
                "Make": "Honda",
                "Model": "Civic",
                "Year": 2019,
                "Vehicle Number": "XYZ789",
            },
        ]

    def add_vehicle(self) -> None:
        """Add a new vehicle to the database."""
        # Implement the logic to add a new vehicle
        pass

    def update_vehicle(self) -> None:
        """Update the selected vehicle."""
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Update", "Update vehicle functionality"
            )

    def delete_vehicle(self) -> None:
        """Delete the selected vehicle."""
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Delete", "Delete vehicle functionality"
            )

    def search_items(self) -> None:
        """Filter items based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        # Filter all items
        self.filtered_items = self.all_items.copy()
        if search_text:
            self.filtered_items = [
                item
                for item in self.all_items
                if (
                    (
                        criteria == "id"
                        and search_text in str(item["ID"]).lower()
                    )
                    or (
                        criteria == "make"
                        and search_text in item["Make"].lower()
                    )
                    or (
                        criteria == "model"
                        and search_text in item["Model"].lower()
                    )
                    or (
                        criteria == "year"
                        and search_text in str(item["Year"]).lower()
                    )
                    or (
                        criteria == "vehicle number"
                        and search_text in item["Vehicle Number"].lower()
                    )
                )
            ]

        # Reload the table with filtered data
        self.load_items()

    def load_items(self) -> None:
        """Load items into the table."""
        self.customer_table.setRowCount(
            len(self.filtered_items) + 1
        )  # +1 for header
        self.customer_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Make", "Model", "Year", "Vehicle Number"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)

        # Populate data
        for row, item in enumerate(self.filtered_items, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(item["ID"]))
            )
            self.customer_table.setItem(row, 1, QTableWidgetItem(item["Make"]))
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(item["Model"])
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(str(item["Year"]))
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(item["Vehicle Number"])
            )

        # Maintain table appearance
        self.customer_table.resizeColumnsToContents()
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.customer_table.rowCount()):
            self.customer_table.setRowHeight(row, row_height)

    def show_context_menu(self, position):
        """Show context menu for table row."""
        row = self.customer_table.rowAt(position.y())
        if row >= 0:  # Ensure a valid row is selected
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            self.apply_styles(context_menu)

            # Create styled update action
            update_action = context_menu.addAction("✏️ Update")
            update_action.setStatusTip("Update selected item")

            context_menu.addSeparator()

            # Create styled delete action
            delete_action = context_menu.addAction("🗑️ Delete")
            delete_action.setStatusTip("Delete selected item")

            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_vehicle()
            elif action == delete_action:
                self.delete_vehicle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    vehicle_gui = VehicleGUI(main_window)
    main_window.setCentralWidget(vehicle_gui)
    main_window.setWindowTitle("Vehicle Management System")
    main_window.resize(800, 600)

    # Apply styles to both main window and central widget
    vehicle_gui.apply_styles(main_window)
    vehicle_gui.apply_styles()

    main_window.show()
    sys.exit(app.exec())
