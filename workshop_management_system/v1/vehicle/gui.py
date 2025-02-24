"""Vehicle GUI Module."""

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTableWidgetItem,  # Add this import
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.database.session import get_session
from workshop_management_system.v1.base.gui import (
    BaseDialog,
    BaseManagementGUI,
)
from workshop_management_system.v1.base.model import PaginationBase
from workshop_management_system.v1.customer.gui import (
    CustomerDialog,  # Add this import
)
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView


class CustomerComboBox(QComboBox):
    """Custom ComboBox for customer selection."""

    def __init__(self, parent=None) -> None:
        """Initialize CustomerComboBox."""
        super().__init__(parent)
        self.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
                background-color: white;
                color: black;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
                background: skyblue;
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: skyblue;
                selection-color: white;
            }
        """
        )
        self.customer_ids = []
        self.blockSignals(True)  # Block signals during initial load

        # Add initial items
        self.addItem("Select a customer...")  # Index 0
        self.customer_ids.append(None)
        self.addItem("Add new customer...")  # Index 1
        self.customer_ids.append("new")

        # Load existing customers
        self.load_customers()
        self.blockSignals(False)

        # Connect the selection change event
        self.currentIndexChanged.connect(self.check_new_customer)

    def load_customers(self) -> None:
        """Load customers into combo box."""
        try:
            with Session(engine) as session:
                customers = session.exec(select(Customer)).all()
                self.clear()
                self.customer_ids.clear()

                # Add default items
                self.addItem("Select a customer...")
                self.customer_ids.append(None)
                self.addItem("Add new customer...")
                self.customer_ids.append("new")

                for customer in customers:
                    self.customer_ids.append(customer.id)
                    display_text = f"{customer.name} ({customer.contact_no})"
                    self.addItem(display_text)
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load customers: {e!s}"
            )

    def get_selected_customer_id(self) -> int | str | None:
        """Get the ID of the selected customer."""
        current_index = self.currentIndex()
        if current_index == 1:  # Add new customer (now second item)
            return "new"
        if current_index > 1 and current_index < len(self.customer_ids):
            return self.customer_ids[current_index]
        return None

    def check_new_customer(self) -> None:
        """Check if 'Add new customer...' is selected and show dialog."""
        if self.currentIndex() == 1:
            dialog = CustomerDialog(self)
            dialog.setModal(True)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                try:
                    with Session(engine) as session:
                        new_customer = Customer(**data)
                        session.add(new_customer)
                        session.commit()
                        self.blockSignals(True)  # Block signals during reload
                        self.load_customers()
                        # Find and set the index of the new customer
                        for i in range(self.count()):
                            if self.itemText(i).startswith(new_customer.name):
                                self.setCurrentIndex(i)
                                break
                        self.blockSignals(False)  # Unblock signals
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Failed to add customer: {e!s}"
                    )
                    self.blockSignals(True)
                    self.setCurrentIndex(0)
                    self.blockSignals(False)
            else:
                self.blockSignals(True)
                self.setCurrentIndex(0)
                self.blockSignals(False)

    def set_customer_by_id(self, customer_id: int) -> None:
        """Set the combo box to the customer with the given ID."""
        if customer_id in self.customer_ids:
            self.setCurrentIndex(self.customer_ids.index(customer_id))
        else:
            self.setCurrentIndex(0)  # Default to "Select a customer..."


class VehicleDialog(BaseDialog):
    """Dialog for adding/updating a vehicle."""

    def __init__(self, parent=None, vehicle_data: dict | None = None) -> None:
        """Initialize the Vehicle Dialog."""
        super().__init__(parent, vehicle_data)
        self.setWindowTitle("Vehicle Details")

    def setup_form(self) -> None:
        """Setup the vehicle form fields."""
        # Create input fields with validation
        self.make_input = QLineEdit(self)
        self.model_input = QLineEdit(self)
        self.year_input = QLineEdit(self)
        self.year_input.setValidator(QIntValidator(1886, 9999))
        self.vehicle_number_input = QLineEdit(self)
        self.vehicle_number_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("^[A-Za-z0-9]+$"))
        )
        self.customer_combo = CustomerComboBox(self)

        # Add fields to form
        self.form_layout.addRow("Make:", self.make_input)
        self.form_layout.addRow("Model:", self.model_input)
        self.form_layout.addRow("Year:", self.year_input)
        self.form_layout.addRow("Vehicle Number:", self.vehicle_number_input)
        self.form_layout.addRow("Customer:", self.customer_combo)

        if hasattr(self, "data") and self.data:
            self.set_data(self.data)

    def validate(self) -> None:
        """Validate form inputs."""
        if not self.make_input.text().strip():
            QMessageBox.warning(self, "Error", "Make is required!")
            return

        if not self.model_input.text().strip():
            QMessageBox.warning(self, "Error", "Model is required!")
            return

        try:
            year = int(self.year_input.text())
            if not (1886 <= year <= 9999):
                QMessageBox.warning(
                    self, "Error", "Year must be between 1886 and 9999!"
                )
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid year format!")
            return

        if not self.vehicle_number_input.text().strip():
            QMessageBox.warning(self, "Error", "Vehicle Number is required!")
            return

        if not self.customer_combo.get_selected_customer_id():
            QMessageBox.warning(self, "Error", "Please select a customer!")
            return

        self.accept()

    def set_data(self, vehicle_data: dict) -> None:
        """Set the dialog's fields with existing vehicle data."""
        self.make_input.setText(str(vehicle_data.get("make", "")))
        self.model_input.setText(str(vehicle_data.get("model", "")))
        self.year_input.setText(str(vehicle_data.get("year", "")))
        self.vehicle_number_input.setText(
            str(vehicle_data.get("vehicle_number", ""))
        )
        if vehicle_data.get("customer_id"):
            self.customer_combo.set_customer_by_id(vehicle_data["customer_id"])

    def get_data(self) -> dict:
        """Get the data from the dialog."""
        return {
            "make": self.make_input.text().strip(),
            "model": self.model_input.text().strip(),
            "year": int(self.year_input.text()),
            "vehicle_number": self.vehicle_number_input.text().strip(),
            "customer_id": self.customer_combo.get_selected_customer_id(),
        }


class VehicleGUI(BaseManagementGUI):
    """Vehicle GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Vehicle GUI."""
        self.vehicle_view = VehicleView(model=Vehicle)
        super().__init__(parent)

    def setup_header(self, main_layout) -> None:
        """Setup vehicle management header."""
        super().setup_header(main_layout)
        self.findChild(QLabel).setText("Vehicle Management")

    def setup_search(self, main_layout) -> None:
        """Setup vehicle search components."""
        super().setup_search(main_layout)
        self.search_input.setPlaceholderText("Search vehicles...")
        self.search_criteria.addItems(
            ["Make", "Model", "Vehicle Number", "Customer Name"]
        )
        self.search_input.textChanged.connect(self.search_vehicles)
        self.search_criteria.currentTextChanged.connect(self.search_vehicles)

    def search_vehicles(self) -> None:
        """Filter vehicles based on search criteria."""
        self.current_page = 1
        self.load_records(refresh_all=False)

    def add_record(self) -> None:
        """Add a new vehicle record."""
        try:
            dialog = VehicleDialog(self)
            if dialog.exec() == VehicleDialog.DialogCode.Accepted:
                with get_session() as session:
                    new_vehicle = Vehicle(**dialog.get_data())
                    self.vehicle_view.create(
                        db_session=session, record=new_vehicle
                    )
                    self.load_records(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Vehicle added successfully!"
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add vehicle: {e!s}"
            )

    def update_record(self) -> None:
        """Update a vehicle record."""
        try:
            selected_row = self.table.currentRow()
            if selected_row <= 0:
                return

            vehicle_id = int(self.table.item(selected_row, 0).text())

            with get_session() as session:
                vehicle = self.vehicle_view.read_by_id(
                    db_session=session, record_id=vehicle_id
                )
                if not vehicle:
                    QMessageBox.warning(
                        self, "Not Found", "Vehicle no longer exists"
                    )
                    return

                dialog = VehicleDialog(self)
                dialog.set_data(
                    {
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "year": vehicle.year,
                        "vehicle_number": vehicle.vehicle_number,
                        "customer_id": vehicle.customer_id,
                    }
                )

                if dialog.exec() == VehicleDialog.DialogCode.Accepted:
                    updated_vehicle = Vehicle(**dialog.get_data())
                    self.vehicle_view.update_by_id(
                        db_session=session,
                        record_id=vehicle_id,
                        record=updated_vehicle,
                    )
                    self.load_records(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Vehicle updated successfully!"
                    )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update vehicle: {e!s}"
            )

    def delete_record(self) -> None:
        """Delete a vehicle record."""
        try:
            selected_row = self.table.currentRow()
            if selected_row <= 0:
                return

            vehicle_id = int(self.table.item(selected_row, 0).text())

            if (
                QMessageBox.question(
                    self,
                    "Confirm Delete",
                    "Are you sure you want to delete this vehicle?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                with get_session() as session:
                    if self.vehicle_view.delete_by_id(
                        db_session=session, record_id=vehicle_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Vehicle deleted successfully!"
                        )
                        self.load_records()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Vehicle not found!"
                        )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete vehicle: {e!s}"
            )

    def load_records(self, refresh_all=True) -> None:
        """Load vehicles using backend pagination."""
        try:
            search_text = self.search_input.text().lower()
            search_field = (
                self.search_criteria.currentText().lower()
                if search_text
                else None
            )

            with get_session() as session:
                result: PaginationBase[Vehicle] = self.vehicle_view.read_all(
                    db_session=session,
                    page=self.current_page,
                    limit=self.page_size,
                    search_by=search_field,
                    search_query=search_text,
                )

                self.prev_button.setEnabled(
                    result.previous_record_id is not None
                )
                self.next_button.setEnabled(result.next_record_id is not None)
                self._update_table_data(result.records)
                self.update_pagination_buttons(result.total_pages)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def _update_table_data(self, records: list) -> None:
        """Update table data with provided records."""
        self.table.setRowCount(len(records) + 1)  # +1 for header
        self.table.setColumnCount(6)

        # Set headers
        headers: list[str] = [
            "ID",
            "Make",
            "Model",
            "Year",
            "Vehicle Number",
            "Customer",
        ]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.table.setItem(0, col, item)

        # Populate data
        for row, vehicle in enumerate(records, start=1):
            with Session(engine) as session:
                customer = session.exec(
                    select(Customer).where(Customer.id == vehicle.customer_id)
                ).first()
                customer_name = customer.name if customer else ""

            self.table.setItem(row, 0, QTableWidgetItem(str(vehicle.id)))
            self.table.setItem(row, 1, QTableWidgetItem(vehicle.make))
            self.table.setItem(row, 2, QTableWidgetItem(vehicle.model))
            self.table.setItem(row, 3, QTableWidgetItem(str(vehicle.year)))
            self.table.setItem(
                row, 4, QTableWidgetItem(vehicle.vehicle_number)
            )
            self.table.setItem(row, 5, QTableWidgetItem(customer_name))

        # Update table appearance
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

        # Set consistent row heights
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)

    def show_context_menu(self, position) -> None:
        """Show context menu for table row."""
        row = self.table.rowAt(position.y())
        if row > 0:  # Skip header row
            self.table.selectRow(row)
            context_menu = QMenu(self)

            update_action = context_menu.addAction("✏️ Update")
            update_action.setStatusTip("Update selected vehicle")

            context_menu.addSeparator()

            delete_action = context_menu.addAction("🗑️ Delete")
            delete_action.setStatusTip("Delete selected vehicle")

            action = context_menu.exec(self.table.mapToGlobal(position))
            if action == update_action:
                self.update_record()
            elif action == delete_action:
                self.delete_record()

    def setup_buttons(self, main_layout) -> None:
        """Setup vehicle management buttons."""
        super().setup_buttons(main_layout)  # This will add all base buttons


if __name__ == "__main__":
    app = QApplication([])
    window = VehicleGUI()
    window.show()
    app.exec()
