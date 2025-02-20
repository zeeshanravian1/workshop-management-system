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
    QHeaderView,  # Add this import
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,  # Add this import
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.database.session import get_session
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
        """)
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
        self.current_page = 1
        self.page_size = 15
        self.vehicle_view = VehicleView(model=Vehicle)

        # Update theme to match CustomerGUI
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: skyblue;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                margin: 0px;
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
            }
            QTableWidget::item:selected {
                background-color: skyblue;
                color: white;
            }
        """)

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
        table_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        table_layout.setSpacing(0)  # Remove spacing

        # Set minimum size for table frame
        table_frame.setMinimumHeight(300)
        table_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Update vehicle table configuration
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.vehicle_table.setAlternatingRowColors(True)
        self.vehicle_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.vehicle_table.setMinimumHeight(300)  # Add minimum height to table

        # Update table styling to exactly match CustomerGUI
        self.vehicle_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """)
        self.vehicle_table.verticalHeader().setVisible(False)
        self.vehicle_table.horizontalHeader().setVisible(False)
        self.vehicle_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.vehicle_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.vehicle_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        table_layout.addWidget(self.vehicle_table)
        main_layout.addWidget(table_frame, 1)  # Add stretch factor

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

        # Replace the old pagination section with new pagination frame
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setSpacing(5)

        # Previous button
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Page number buttons container
        self.page_buttons_layout = QHBoxLayout()
        self.page_buttons_layout.setSpacing(5)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addLayout(self.page_buttons_layout)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(pagination_frame)

        self.load_vehicles()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def _update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        # Clear existing buttons
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_page = self.current_page

        # Always show first page
        self.add_page_button(1)

        if total_pages > 7:
            # Show ellipsis after first page if needed
            if current_page > 3:
                self.page_buttons_layout.addWidget(self._create_ellipsis())

            # Show pages around current page
            if current_page <= 3:
                # Near start - show first few pages
                for page in range(2, 6):
                    self.add_page_button(page)
            elif current_page >= total_pages - 2:
                # Near end - show last few pages
                for page in range(total_pages - 4, total_pages):
                    self.add_page_button(page)
            else:
                # In middle - show pages around current
                for page in range(current_page - 2, current_page + 3):
                    if 1 < page < total_pages:
                        self.add_page_button(page)

            # Show ellipsis before last page if needed
            if current_page < total_pages - 3:
                self.page_buttons_layout.addWidget(self._create_ellipsis())

        else:
            # For small number of pages, show all pages
            for page in range(2, total_pages + 1):
                self.add_page_button(page)

        # Always show last page if more than one page
        if total_pages > 1:
            self.add_page_button(total_pages)

    def _create_ellipsis(self):
        """Create ellipsis button for pagination."""
        ellipsis = QPushButton("...")
        ellipsis.setEnabled(False)
        ellipsis.setFixedSize(40, 40)
        ellipsis.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-weight: bold;
                min-width: 40px;
            }
        """)
        return ellipsis

    def add_page_button(self, page_num: int) -> None:
        """Add a single page button."""
        button = QPushButton(str(page_num))
        button.setFixedSize(40, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumWidth(40)
        button.setMaximumWidth(40)

        if page_num == self.current_page:
            button.setStyleSheet("""
                QPushButton {
                    background-color: skyblue;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    min-width: 40px;
                    max-width: 40px;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    min-width: 40px;
                    max-width: 40px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

        button.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_buttons_layout.addWidget(button)

    def load_vehicles(self, refresh_all=True) -> None:
        """Load vehicles using backend pagination."""
        try:
            search_text = self.search_input.text().lower()
            search_field = (
                self.search_criteria.currentText().lower()
                if search_text
                else None
            )

            with get_session() as session:
                # Properly using BaseView's read_all method
                result = self.vehicle_view.read_all(
                    db_session=session,
                    page=self.current_page,
                    limit=self.page_size,
                    search_by=search_field,
                    search_query=search_text,
                )

                # Correct usage of PaginationBase attributes
                self.prev_button.setEnabled(
                    result.previous_record_id is not None
                )
                self.next_button.setEnabled(result.next_record_id is not None)
                self._update_table_data(result.records)
                self._update_pagination_buttons(result.total_pages)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def next_page(self) -> None:
        """Load the next page of vehicles."""
        self.current_page += 1
        self.load_vehicles(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of vehicles."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_vehicles(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if (
            1 <= page_number <= self.pagination["total_pages"]
            and page_number != self.current_page
        ):
            self.current_page = page_number
            self.load_vehicles(refresh_all=False)

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
        ]  # Remove customer from fields list since we'll add it separately

        # Add regular input fields
        for field in fields:
            field_name, label = field[0], field[1]
            widget_class = field[2]

            input_field = widget_class(dialog)
            if len(field) > 3:
                input_field.setValidator(field[3])

            if vehicle and field_name != "customer":
                input_field.setText(str(getattr(vehicle, field_name)))

            inputs[field_name] = input_field
            layout.addRow(f"{label}:", input_field)

        # Add customer selection
        customer_combo = CustomerComboBox(dialog)
        if vehicle and vehicle.customer_id:
            customer_combo.set_customer_by_id(vehicle.customer_id)
        else:
            customer_combo.setCurrentIndex(0)
        inputs["customer"] = customer_combo
        layout.addRow("Customer:", customer_combo)

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
        """Add vehicle using BaseView."""
        try:
            dialog, inputs = self.create_input_dialog("Add Vehicle")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                with get_session() as session:
                    # Create vehicle with only VehicleBase fields
                    new_vehicle = Vehicle(
                        make=inputs["make"].text(),
                        model=inputs["model"].text(),
                        year=int(inputs["year"].text()),
                        vehicle_number=inputs["vehicle_number"].text(),
                        customer_id=inputs[
                            "customer"
                        ].get_selected_customer_id(),
                    )
                    self.vehicle_view.create(
                        db_session=session, record=new_vehicle
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle added successfully!"
                    )
                    self.load_vehicles(refresh_all=True)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add vehicle: {e!s}"
            )

    def update_vehicle(self) -> None:
        """Update vehicle using BaseView."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row <= 0:
                QMessageBox.warning(
                    self, "Warning", "Please select a vehicle to update."
                )
                return

            vehicle_id = int(self.vehicle_table.item(selected_row, 0).text())

            with get_session() as session:
                # Use BaseView's read_by_id method
                vehicle = self.vehicle_view.read_by_id(
                    db_session=session, record_id=vehicle_id
                )
                if not vehicle:
                    QMessageBox.warning(self, "Error", "Vehicle not found.")
                    return

                dialog, inputs = self.create_input_dialog(
                    "Update Vehicle", vehicle
                )
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    customer_id = inputs["customer"].get_selected_customer_id()
                    updated_vehicle = Vehicle(
                        make=inputs["make"].text(),
                        model=inputs["model"].text(),
                        year=int(inputs["year"].text()),
                        vehicle_number=inputs["vehicle_number"].text(),
                        customer_id=customer_id,
                    )
                    # Use BaseView's update_by_id method
                    self.vehicle_view.update_by_id(
                        db_session=session,
                        record_id=vehicle_id,
                        record=updated_vehicle,
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle updated successfully!"
                    )
                    self.load_vehicles(refresh_all=True)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update vehicle: {e!s}"
            )

    def delete_vehicle(self) -> None:
        """Delete vehicle using BaseView."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row <= 0:
                return

            vehicle_id = int(self.vehicle_table.item(selected_row, 0).text())

            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this vehicle?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                with get_session() as session:
                    # Use BaseView's delete_by_id method
                    if self.vehicle_view.delete_by_id(
                        db_session=session, record_id=vehicle_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Vehicle deleted successfully!"
                        )
                        self.load_vehicles()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Vehicle not found!"
                        )

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
        # Remove local filtering as it's handled by BaseView
        self.current_page = 1
        self.load_vehicles(refresh_all=True)

    def get_customer_name(self, vehicle) -> str:
        """Get customer name for a vehicle."""
        try:
            with Session(engine) as session:
                customer = session.exec(
                    select(Customer).where(Customer.id == vehicle.customer_id)
                ).first()
                return customer.name if customer else ""
        except Exception:
            return ""

    def _update_table_data(self, records):
        """Update table data to match VehicleBase model fields."""
        self.vehicle_table.setRowCount(len(records) + 1)
        self.vehicle_table.setColumnCount(6)

        # Headers match VehicleBase fields
        headers = ["ID", "Make", "Model", "Year", "Vehicle Number", "Customer"]
        # Set headers
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.vehicle_table.setItem(0, col, item)

        # Populate data matching VehicleBase fields
        for row, vehicle in enumerate(records, start=1):
            with Session(engine) as session:
                customer = session.exec(
                    select(Customer).where(Customer.id == vehicle.customer_id)
                ).first()
                customer_name = customer.name if customer else ""

            self.vehicle_table.setItem(
                row, 0, QTableWidgetItem(str(vehicle.id))
            )
            self.vehicle_table.setItem(row, 1, QTableWidgetItem(vehicle.make))
            self.vehicle_table.setItem(row, 2, QTableWidgetItem(vehicle.model))
            self.vehicle_table.setItem(
                row, 3, QTableWidgetItem(str(vehicle.year))
            )
            self.vehicle_table.setItem(
                row, 4, QTableWidgetItem(vehicle.vehicle_number)
            )
            self.vehicle_table.setItem(row, 5, QTableWidgetItem(customer_name))

        # Maintain table appearance
        self.vehicle_table.resizeColumnsToContents()
        self.vehicle_table.horizontalHeader().setStretchLastSection(True)
        self.vehicle_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.vehicle_table.rowCount()):
            self.vehicle_table.setRowHeight(row, row_height)


if __name__ == "__main__":  # Fixed syntax error here - added == operator
    app = QApplication([])
    window = VehicleGUI()
    window.show()
    app.exec()
