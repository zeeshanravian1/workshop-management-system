"""Customer GUI Module.

Description:
- This module provides the GUI for managing customers.

"""

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QFont, QRegularExpressionValidator
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
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


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
        self.mobile_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.address_input = QLineEdit(self)

        # Set validators
        mobile_regex = QRegularExpression(r"^\+?\d{10,15}$")
        self.mobile_input.setValidator(
            QRegularExpressionValidator(mobile_regex, self)
        )
        email_regex = QRegularExpression(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        self.email_input.setValidator(
            QRegularExpressionValidator(email_regex, self)
        )

        # Add fields to form
        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Mobile:", self.mobile_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Address:", self.address_input)

        # Add OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def validate_and_accept(self):
        """Validate inputs and accept the dialog if valid."""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Name is required!")
            return
        if not self.mobile_input.hasAcceptableInput():
            QMessageBox.warning(
                self, "Invalid Input", "Invalid mobile number!"
            )
            return
        if not self.email_input.hasAcceptableInput():
            QMessageBox.warning(
                self, "Invalid Input", "Invalid email address!"
            )
            return
        if not self.address_input.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Address is required!")
            return
        self.accept()

    def set_data(self, customer_data: dict) -> None:
        """Set the dialog's fields with existing customer data."""
        self.name_input.setText(customer_data.get("name", ""))
        self.mobile_input.setText(customer_data.get("mobile_number", ""))
        self.email_input.setText(customer_data.get("email", ""))
        self.address_input.setText(customer_data.get("address", ""))

    def get_data(self) -> dict:
        """Get the data from the dialog."""
        return {
            "name": self.name_input.text().strip(),
            "mobile_number": self.mobile_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.address_input.text().strip(),
        }


class CustomerGUI(QWidget):
    """Customer GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Customer GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        # Update pagination to match PaginationBase
        self.pagination = {
            "current_page": 1,
            "limit": 15,  # Keep original page size
            "total_pages": 0,
            "total_records": 0,
            "next_record_id": None,
            "previous_record_id": None,
            "records": [],
        }
        # Keep original properties for compatibility
        self.page_size = self.pagination["limit"]
        self.current_page = self.pagination["current_page"]
        self.all_customers = []
        self.filtered_customers = []

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
            }
            QLabel {
                color: black;
            }
        """)

        self.customer_view = CustomerView(model=Customer)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Customer Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.textChanged.connect(self.search_customers)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(["Name", "Mobile", "Email", "Address"])
        self.search_criteria.currentTextChanged.connect(self.search_customers)

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_criteria)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Buttons container
        buttons_layout = QHBoxLayout()

        # Back button (left aligned)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Add Customer button (right aligned)
        add_button = QPushButton("Add Customer")
        add_button.clicked.connect(self.add_customer)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Add buttons to the layout
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()  # This creates space between the buttons
        buttons_layout.addWidget(add_button)

        main_layout.addLayout(buttons_layout)

        # Table Frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.NoFrame)
        table_layout = QVBoxLayout(table_frame)

        # Set minimum size for table frame
        table_frame.setMinimumHeight(300)
        table_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.customer_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
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
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.horizontalHeader().setVisible(False)
        self.customer_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.customer_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.customer_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.customer_table.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.customer_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        table_layout.addWidget(self.customer_table)
        main_layout.addWidget(table_frame)

        # Replace the pagination frame section with:
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

        self.load_customers()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def search_customers(self) -> None:
        """Filter customers based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        # Filter all customers
        self.filtered_customers = self.all_customers.copy()
        if search_text:
            self.filtered_customers = [
                customer
                for customer in self.all_customers
                if (
                    (
                        criteria == "name"
                        and search_text in customer.name.lower()
                    )
                    or (
                        criteria == "mobile"
                        and search_text in customer.mobile_number.lower()
                    )
                    or (
                        criteria == "email"
                        and search_text in customer.email.lower()
                    )
                    or (
                        criteria == "address"
                        and search_text in customer.address.lower()
                    )
                )
            ]

        # Reset pagination
        self.pagination["current_page"] = 1
        self.current_page = 1  # Keep in sync
        self.pagination["total_records"] = len(self.filtered_customers)

        # Reload the table with filtered data
        self.load_customers(refresh_all=False)

    def update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        # Clear existing buttons
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_page = self.pagination["current_page"]

        # Always show first page
        self.add_page_button(1)

        # Calculate page range to show
        if total_pages > 7:
            # Show ellipsis after first page if needed
            if current_page > 3:
                self.page_buttons_layout.addWidget(self._create_ellipsis())

            # Calculate range of pages to show around current page
            start_page = max(2, current_page - 2)
            end_page = min(total_pages - 1, current_page + 2)

            # Show pages
            for page in range(start_page, end_page + 1):
                self.add_page_button(page)

            # Show ellipsis before last page if needed
            if current_page < total_pages - 2:
                self.page_buttons_layout.addWidget(self._create_ellipsis())

        else:
            # If total pages <= 7, show all pages
            for page in range(2, total_pages + 1):
                self.add_page_button(page)

        # Always show last page if more than one page
        if total_pages > 1 and current_page != total_pages:
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

        if page_num == self.pagination["current_page"]:
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

    def load_customers(self, refresh_all=True) -> None:
        """Load customers from the database with pagination."""
        try:
            with Session(engine) as session:
                if refresh_all:
                    self.all_customers = self.customer_view.read_all(
                        db_session=session
                    )
                    self.filtered_customers = self.all_customers.copy()

                total_records = len(self.filtered_customers)
                total_pages = (
                    total_records + self.pagination["limit"] - 1
                ) // self.pagination["limit"]

                # Update pagination state
                self.pagination.update(
                    {
                        "total_records": total_records,
                        "total_pages": total_pages,
                    }
                )

                # Calculate page data
                start_idx = (
                    self.pagination["current_page"] - 1
                ) * self.pagination["limit"]
                end_idx = start_idx + self.pagination["limit"]
                current_page_records = self.filtered_customers[
                    start_idx:end_idx
                ]
                self.pagination["records"] = current_page_records

                # Update next/previous record IDs
                if end_idx < total_records:
                    self.pagination["next_record_id"] = (
                        self.filtered_customers[end_idx].id
                    )
                else:
                    self.pagination["next_record_id"] = None

                if start_idx > 0:
                    self.pagination["previous_record_id"] = (
                        self.filtered_customers[start_idx - 1].id
                    )
                else:
                    self.pagination["previous_record_id"] = None

                # Update table content
                self._update_table_data(current_page_records)

                # Update pagination buttons
                self.update_pagination_buttons(total_pages)

                # Enable/disable navigation buttons
                self.prev_button.setEnabled(
                    self.pagination["previous_record_id"] is not None
                )
                self.next_button.setEnabled(
                    self.pagination["next_record_id"] is not None
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def _update_table_data(self, records):
        """Update table data while preserving table properties."""
        self.customer_table.setRowCount(len(records) + 1)  # +1 for header
        self.customer_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Name", "Mobile", "Email", "Address"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)

        # Populate data
        for row, customer in enumerate(records, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(customer.id))
            )
            self.customer_table.setItem(
                row, 1, QTableWidgetItem(customer.name)
            )
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(customer.mobile_number)
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(customer.email)
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(customer.address)
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

    def next_page(self) -> None:
        """Load the next page of customers."""
        if self.pagination["next_record_id"] is not None:
            self.pagination["current_page"] += 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_customers(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of customers."""
        if self.pagination["previous_record_id"] is not None:
            self.pagination["current_page"] -= 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_customers(refresh_all=False)

    def go_to_page(self, page_number):
        """Navigate to specific page number."""
        if (
            1 <= page_number <= self.pagination["total_pages"]
            and page_number != self.pagination["current_page"]
        ):
            self.pagination["current_page"] = page_number
            self.current_page = page_number  # Keep in sync
            self.load_customers(refresh_all=False)

    def add_customer(self) -> None:
        """Add a new customer to the database."""
        try:
            dialog = CustomerDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()

                # Validate inputs
                if not all(data.values()):
                    QMessageBox.warning(
                        self, "Invalid Input", "All fields are required!"
                    )
                    return

                with Session(engine) as session:
                    new_customer = Customer(**data)
                    self.customer_view.create(
                        db_session=session, record=new_customer
                    )
                    QMessageBox.information(
                        self, "Success", "Customer added successfully!"
                    )
                    self.load_customers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add customer: {e!s}"
            )

    def update_customer(self) -> None:
        """Update an existing customer."""
        try:
            selected_row = self.customer_table.currentRow()
            if selected_row <= 0:  # Skip header row
                return

            item = self.customer_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected customer ID is invalid."
                )
                return

            customer_id = int(item.text())

            # Get current values
            current_data = {
                "name": self.customer_table.item(selected_row, 1).text(),
                "mobile_number": self.customer_table.item(
                    selected_row, 2
                ).text(),
                "email": self.customer_table.item(selected_row, 3).text(),
                "address": self.customer_table.item(selected_row, 4).text(),
            }

            dialog = CustomerDialog(self)
            dialog.set_data(current_data)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()

                # Validate inputs
                if not all(data.values()):
                    QMessageBox.warning(
                        self, "Invalid Input", "All fields are required!"
                    )
                    return

                with Session(engine) as session:
                    customer = self.customer_view.read_by_id(
                        db_session=session, record_id=customer_id
                    )
                    if customer:
                        for field, value in data.items():
                            setattr(customer, field, value)
                        self.customer_view.update(
                            db_session=session,
                            record_id=customer_id,
                            record=customer,
                        )
                        QMessageBox.information(
                            self, "Success", "Customer updated successfully!"
                        )
                        self.load_customers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update customer: {e!s}"
            )

    def delete_customer(self) -> None:
        """Delete a customer from the database."""
        try:
            selected_row = self.customer_table.currentRow()
            if selected_row <= 0:  # Skip header row
                return

            item = self.customer_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected customer ID is invalid."
                )
                return
            customer_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Customer",
                "Are you sure you want to delete this customer?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.customer_view.delete(
                        db_session=session, record_id=int(customer_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Customer deleted successfully!"
                    )
                    self.load_customers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete customer: {e!s}"
            )

    def show_context_menu(self, position):
        """Show context menu for table row."""
        row = self.customer_table.rowAt(position.y())
        if row > 0:  # Skip header row
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            context_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 25px;
                    color: black;
                    border-radius: 4px;
                    margin: 2px 5px;
                }
                QMenu::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background: #cccccc;
                    margin: 5px 0px;
                }
            """)

            # Create styled update action
            update_action = context_menu.addAction("✏️ Update")
            update_action.setStatusTip("Update selected customer")

            context_menu.addSeparator()

            # Create styled delete action
            delete_action = context_menu.addAction("🗑️ Delete")
            delete_action.setStatusTip("Delete selected customer")

            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_customer()
            elif action == delete_action:
                self.delete_customer()

    def on_row_selected(self):
        """Handle row selection changes."""
        if self.customer_table.selectedItems():
            current_row = self.customer_table.currentRow()
            if current_row == 0:  # If header row is selected
                self.customer_table.clearSelection()
            else:
                # Select entire row
                self.customer_table.selectRow(current_row)


if __name__ == "__main__":
    app = QApplication([])
    window = CustomerGUI()
    window.show()
    app.exec()
