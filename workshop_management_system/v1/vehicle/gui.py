"""Vehicle GUI Module."""

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QFont, QIntValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView


class CustomerDialog(QDialog):
    """Dialog for adding/updating a customer."""

    def __init__(self, parent=None) -> None:
        """Initialize the Customer Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Customer Details")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QFormLayout {
                spacing: 15px;
            }
        """)
        self.form_layout = QFormLayout(self)

        # Create input fields
        self.name_input = QLineEdit(self)
        self.mobile_number_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.address_input = QLineEdit(self)

        # Add fields to layout
        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Mobile Number:", self.mobile_number_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Address:", self.address_input)

        # Add buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def get_data(self):
        """Get the data from the dialog."""
        return {
            "name": self.name_input.text(),
            "mobile_number": self.mobile_number_input.text(),
            "email": self.email_input.text(),
            "address": self.address_input.text(),
        }


class CustomerComboBox(QComboBox):
    """Custom ComboBox for customer selection."""

    def __init__(self, parent=None) -> None:
        """Initialize CustomerComboBox."""
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
                background-color: white;
                color: black;  # Set text color to black
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                border: 2px solid #4CAF50;
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
                margin-top: -5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
        """)
        self.customer_ids = []
        self.blockSignals(True)  # Block signals during initial load
        self.load_customers()
        self.blockSignals(False)
        self.currentIndexChanged.connect(self.check_new_customer)

    def load_customers(self) -> None:
        """Load customers into combo box."""
        try:
            with Session(engine) as session:
                customers = session.exec(select(Customer)).all()
                self.clear()
                self.customer_ids.clear()

                # Changed order: first "Select customer", then "Add new"
                self.addItem("Select a customer...")
                self.customer_ids.append(None)
                self.addItem("Add new customer...")
                self.customer_ids.append("new")

                for customer in customers:
                    self.customer_ids.append(customer.id)
                    display_text = (
                        f"{customer.name} ({customer.mobile_number})"
                    )
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
        if self.currentIndex() == 1:  # "Add new customer..." option
            dialog = CustomerDialog(self)
            dialog.setModal(True)  # Make dialog modal
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


class VehicleGUI(QWidget):
    """Vehicle GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Vehicle GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
                min-width: 125px;
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: green;
                color: white;
            }
            QLabel {
                color: black;
            }
        """)

        self.vehicle_view = VehicleView(model=Vehicle)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Vehicle Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search vehicles...")
        self.search_input.textChanged.connect(self.search_vehicles)

        self.search_criteria = QComboBox()
        # Update search criteria to match actual table columns
        self.search_criteria.addItems(
            ["Make", "Model", "Vehicle Number", "Customer Name"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_vehicles)

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_criteria)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        main_layout.addWidget(
            back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Table Frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.NoFrame)
        table_layout = QVBoxLayout(table_frame)

        # Vehicle table
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.vehicle_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.vehicle_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
            }
        """)
        self.vehicle_table.verticalHeader().setVisible(False)
        self.vehicle_table.horizontalHeader().setVisible(False)
        self.vehicle_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.vehicle_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.vehicle_table.horizontalHeader().setStretchLastSection(True)
        self.vehicle_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_layout.addWidget(self.vehicle_table)
        main_layout.addWidget(table_frame)

        # Button Frame
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.Shape.StyledPanel)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # CRUD Buttons
        buttons = [
            ("Load Vehicles", self.load_vehicles),
            ("Add Vehicle", self.add_vehicle),
            ("Update Vehicle", self.update_vehicle),
            ("Delete Vehicle", self.delete_vehicle),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_vehicles()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_vehicles(self) -> None:
        """Load vehicles from the database and display them in the table."""
        try:
            with Session(engine) as session:
                vehicles = self.vehicle_view.read_all(db_session=session)
                self.vehicle_table.setRowCount(len(vehicles) + 1)
                self.vehicle_table.setColumnCount(8)

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Make",
                    "Model",
                    "Year",
                    "Vehicle Number",
                    "Chassis Number",
                    "Engine Number",
                    "Customer Name",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.vehicle_table.setItem(0, col, item)

                # Set the height of the first row
                self.vehicle_table.setRowHeight(0, 40)

                for row, vehicle in enumerate(vehicles, start=1):
                    customer = session.exec(
                        select(Customer).where(
                            Customer.id == vehicle.customer_id
                        )
                    ).first()
                    self.vehicle_table.setItem(
                        row, 0, QTableWidgetItem(str(vehicle.id))
                    )
                    self.vehicle_table.setItem(
                        row, 1, QTableWidgetItem(vehicle.make)
                    )
                    self.vehicle_table.setItem(
                        row, 2, QTableWidgetItem(vehicle.model)
                    )
                    self.vehicle_table.setItem(
                        row, 3, QTableWidgetItem(str(vehicle.year))
                    )
                    self.vehicle_table.setItem(
                        row, 4, QTableWidgetItem(vehicle.vehicle_number)
                    )
                    self.vehicle_table.setItem(
                        row, 5, QTableWidgetItem(vehicle.chassis_number)
                    )
                    self.vehicle_table.setItem(
                        row, 6, QTableWidgetItem(vehicle.engine_number)
                    )
                    self.vehicle_table.setItem(
                        row,
                        7,
                        QTableWidgetItem(customer.name if customer else ""),
                    )

                # Adjust column widths
                self.vehicle_table.resizeColumnsToContents()
                self.vehicle_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.vehicle_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def create_input_dialog(
        self, title: str, vehicle: Vehicle | None = None
    ) -> tuple[QDialog, dict]:
        """Create a dialog for vehicle input."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)  # Set minimum width for better visibility
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QFormLayout {
                spacing: 15px;
            }
        """)
        layout = QFormLayout(dialog)

        # Create input fields with validation but no placeholder text
        inputs = {}
        fields = [
            ("make", "Make", QLineEdit),
            ("model", "Model", QLineEdit),
            ("year", "Year", QLineEdit, QIntValidator(1886, 9999)),
            (
                "vehicle_number",
                "Vehicle Number",
                QLineEdit,
                QRegularExpressionValidator(
                    QRegularExpression("^[A-Za-z0-9]+$")
                ),
            ),
            (
                "chassis_number",
                "Chassis Number",
                QLineEdit,
                QRegularExpressionValidator(
                    QRegularExpression("^[A-Za-z0-9]+$")
                ),
            ),
            (
                "engine_number",
                "Engine Number",
                QLineEdit,
                QRegularExpressionValidator(
                    QRegularExpression("^[A-Za-z0-9]+$")
                ),
            ),
            ("customer", "Customer", CustomerComboBox),
        ]

        for field in fields:
            field_name, label = field[0], field[1]
            widget_class = field[2]

            input_field = widget_class(dialog)
            if len(field) > 3 and field_name != "customer":
                input_field.setValidator(field[3])

            if vehicle and field_name != "customer":
                input_field.setText(str(getattr(vehicle, field_name)))

            inputs[field_name] = input_field
            layout.addRow(f"{label}:", input_field)

        # Add validation to dialog accept
        def validate_and_accept():
            # Validate Make
            if not inputs["make"].text().strip():
                QMessageBox.warning(dialog, "Error", "Make is required!")
                return

            # Validate Model
            if not inputs["model"].text().strip():
                QMessageBox.warning(dialog, "Error", "Model is required!")
                return

            # Validate Year
            try:
                year = int(inputs["year"].text())
                if not (1886 <= year <= 9999):
                    QMessageBox.warning(
                        dialog, "Error", "Year must be between 1886 and 9999!"
                    )
                    return
            except ValueError:
                QMessageBox.warning(dialog, "Error", "Invalid year format!")
                return

            # Validate Vehicle Number
            if not inputs["vehicle_number"].text().strip():
                QMessageBox.warning(
                    dialog, "Error", "Vehicle Number is required!"
                )
                return

            # Validate Chassis Number
            if not inputs["chassis_number"].text().strip():
                QMessageBox.warning(
                    dialog, "Error", "Chassis Number is required!"
                )
                return

            # Validate Engine Number
            if not inputs["engine_number"].text().strip():
                QMessageBox.warning(
                    dialog, "Error", "Engine Number is required!"
                )
                return

            # Validate Customer Selection
            if not inputs["customer"].get_selected_customer_id():
                QMessageBox.warning(
                    dialog, "Error", "Please select a customer!"
                )
                return

            dialog.accept()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        buttons.accepted.connect(validate_and_accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog, inputs

    def add_new_customer(self) -> int | None:
        """Open the dialog to add a new customer."""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not all(data.values()):
                QMessageBox.warning(
                    self, "Invalid Input", "All fields are required!"
                )
                return None

            try:
                with Session(engine) as session:
                    new_customer = Customer(**data)
                    session.add(new_customer)
                    session.commit()
                    return new_customer.id
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add customer: {e!s}"
                )
                return None
        return None

    def add_vehicle(self) -> None:
        """Add a new vehicle to the database."""
        try:
            dialog, inputs = self.create_input_dialog("Add Vehicle")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                customer_id = inputs["customer"].get_selected_customer_id()
                if customer_id == "new":
                    customer_id = self.add_new_customer()
                    if not customer_id:
                        return
                    inputs["customer"].load_customers()
                    inputs["customer"].setCurrentIndex(
                        inputs["customer"].customer_ids.index(customer_id)
                    )
                elif not customer_id:
                    QMessageBox.critical(
                        self, "Error", "Please select a customer."
                    )
                    return

                with Session(engine) as session:
                    new_vehicle = Vehicle(
                        make=inputs["make"].text(),
                        model=inputs["model"].text(),
                        year=int(inputs["year"].text()),
                        chassis_number=inputs["chassis_number"].text(),
                        vehicle_number=inputs["vehicle_number"].text(),
                        engine_number=inputs["engine_number"].text(),
                        customer_id=customer_id,
                    )
                    self.vehicle_view.create(
                        db_session=session, record=new_vehicle
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle added successfully!"
                    )
                    self.load_vehicles()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add vehicle: {e!s}"
            )

    def update_vehicle(self) -> None:
        """Update an existing vehicle."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a vehicle to update."
                )
                return

            item = self.vehicle_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected vehicle ID is invalid."
                )
                return
            vehicle_id = int(item.text())

            with Session(engine) as session:
                vehicle_obj = self.vehicle_view.read_by_id(
                    db_session=session, record_id=vehicle_id
                )
                if not vehicle_obj:
                    QMessageBox.warning(self, "Error", "Vehicle not found.")
                    return

                dialog, inputs = self.create_input_dialog(
                    "Update Vehicle", vehicle_obj
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    customer_id = inputs["customer"].get_selected_customer_id()
                    if not customer_id:
                        QMessageBox.critical(
                            self, "Error", "Please select a customer."
                        )
                        return

                    vehicle_obj.make = inputs["make"].text()
                    vehicle_obj.model = inputs["model"].text()
                    vehicle_obj.year = int(inputs["year"].text())
                    vehicle_obj.chassis_number = inputs[
                        "chassis_number"
                    ].text()
                    vehicle_obj.vehicle_number = inputs[
                        "vehicle_number"
                    ].text()
                    vehicle_obj.engine_number = inputs["engine_number"].text()
                    vehicle_obj.customer_id = customer_id

                    self.vehicle_view.update(
                        db_session=session,
                        record_id=vehicle_id,
                        record=vehicle_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle updated successfully!"
                    )
                    self.load_vehicles()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update vehicle: {e!s}"
            )

    def delete_vehicle(self) -> None:
        """Delete a vehicle from the database."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a vehicle to delete."
                )
                return

            item = self.vehicle_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected vehicle ID is invalid."
                )
                return
            vehicle_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Vehicle",
                "Are you sure you want to delete this vehicle?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.vehicle_view.delete(
                        db_session=session, record_id=int(vehicle_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle deleted successfully!"
                    )
                    self.load_vehicles()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete vehicle: {e!s}"
            )

    def go_back(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.setCurrentIndex(0)

    def search_vehicles(self) -> None:
        """Filter vehicles based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.vehicle_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                # Update column indices to match actual table structure
                if criteria == "make":
                    cell_text = self.vehicle_table.item(row, 1)
                elif criteria == "model":
                    cell_text = self.vehicle_table.item(row, 2)
                elif criteria == "vehicle number":
                    cell_text = self.vehicle_table.item(row, 4)
                elif criteria == "customer name":
                    cell_text = self.vehicle_table.item(row, 7)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.vehicle_table.setRowHidden(row, not show_row)


if __name__ == "__main__":  # Fixed syntax error here - added == operator
    app = QApplication([])
    window = VehicleGUI()
    window.show()
    app.exec()
