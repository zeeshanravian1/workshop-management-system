"""Vehicle GUI Module.

Description:
- This module provides the GUI components for the vehicle model.

"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView


# Updated: Embedded VehicleDialog class for adding a vehicle with customer dropdown.
class VehicleDialog(QDialog):
    """Dialog to add a new vehicle."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add New Vehicle")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.make_input = QLineEdit()
        self.model_input = QLineEdit()
        self.year_input = QLineEdit()  # Alternatively use QSpinBox
        self.vehicle_number_input = QLineEdit()
        # Replace QLineEdit with QComboBox for customer selection
        self.customer_dropdown = QComboBox()
        # Placeholder items; replace with actual customer fetching logic.
        self.customer_dropdown.addItem("Customer A", 1)
        self.customer_dropdown.addItem("Customer B", 2)

        layout.addRow("Make:", self.make_input)
        layout.addRow("Model:", self.model_input)
        layout.addRow("Year:", self.year_input)
        layout.addRow("Vehicle Number:", self.vehicle_number_input)
        layout.addRow("Customer:", self.customer_dropdown)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """Return entered data."""
        return {
            "make": self.make_input.text().strip(),
            "model": self.model_input.text().strip(),
            "year": int(self.year_input.text().strip() or 0),
            "vehicle_number": self.vehicle_number_input.text().strip(),
            "customer_id": int(self.customer_dropdown.currentData()),
        }


# New: Embedded VehicleUpdateDialog class for updating a vehicle.
class VehicleUpdateDialog(QDialog):
    """Dialog to update an existing vehicle."""

    def __init__(self, initial_data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Update Vehicle")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.make_input = QLineEdit(initial_data.get("make", ""))
        self.model_input = QLineEdit(initial_data.get("model", ""))
        self.year_input = QLineEdit(
            str(initial_data.get("year", ""))
        )  # Alternatively use QSpinBox
        self.vehicle_number_input = QLineEdit(
            initial_data.get("vehicle_number", "")
        )
        # Customer dropdown with initial selection using customer_id from initial_data
        self.customer_dropdown = QComboBox()
        # Placeholder items; replace with actual customer fetching logic.
        self.customer_dropdown.addItem("Customer A", 1)
        self.customer_dropdown.addItem("Customer B", 2)
        # Set current index based on given customer_id
        current_id = initial_data.get("customer_id")
        index = self.customer_dropdown.findData(current_id)
        if index != -1:
            self.customer_dropdown.setCurrentIndex(index)

        layout.addRow("Make:", self.make_input)
        layout.addRow("Model:", self.model_input)
        layout.addRow("Year:", self.year_input)
        layout.addRow("Vehicle Number:", self.vehicle_number_input)
        layout.addRow("Customer:", self.customer_dropdown)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """Return the updated data."""
        return {
            "make": self.make_input.text().strip(),
            "model": self.model_input.text().strip(),
            "year": int(self.year_input.text().strip() or 0),
            "vehicle_number": self.vehicle_number_input.text().strip(),
            "customer_id": int(self.customer_dropdown.currentData()),
        }


class VehicleGUI(BaseGUI):
    """Vehicle GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Vehicle GUI."""
        super().__init__(parent)
        # Insert header label with designated object name
        header = QLabel(
            "Vehicle Management", alignment=Qt.AlignmentFlag.AlignCenter
        )
        header.setObjectName("headerLabel")
        self.layout().insertWidget(0, header)
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
        """Add a new vehicle using an embedded dialog window."""
        dialog = VehicleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            # Here you would typically create a Vehicle instance and add it to the DB.
            # For now, we show the entered data in an information box.
            QMessageBox.information(
                self,
                "Vehicle Data",
                f"Make: {data['make']}\nModel: {data['model']}\nYear: {data['year']}\n"
                f"Vehicle Number: {data['vehicle_number']}\nCustomer ID: {data['customer_id']}",
            )

    def update_vehicle(self) -> None:
        """Update the selected vehicle using an update dialog."""
        selected_row = self.customer_table.currentRow()
        if selected_row < 1:
            QMessageBox.warning(
                self, "Update", "Please select a vehicle to update."
            )
            return

        # Retrieve current data from the selected row
        current_data = {
            "make": self.customer_table.item(selected_row, 1).text(),
            "model": self.customer_table.item(selected_row, 2).text(),
            "year": int(self.customer_table.item(selected_row, 3).text()),
            "vehicle_number": self.customer_table.item(selected_row, 4).text(),
            # For demo, we set a fixed customer id; in a real app, store customer_id in hidden column.
            "customer_id": 1,
        }

        dialog = VehicleUpdateDialog(initial_data=current_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            # Here you would normally update the vehicle record in the database.
            QMessageBox.information(
                self,
                "Updated Vehicle Data",
                f"Make: {updated_data['make']}\nModel: {updated_data['model']}\n"
                f"Year: {updated_data['year']}\nVehicle Number: {updated_data['vehicle_number']}\n"
                f"Customer ID: {updated_data['customer_id']}",
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

    def add(self) -> None:
        """Override base add method to open the add vehicle dialog."""
        self.add_vehicle()


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
