"""Customer GUI Module.

Description:
- This module provides the GUI for managing customers.

"""

from pydantic import ValidationError
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
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

from workshop_management_system.database.session import get_session
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView


class CustomerDialog(QDialog):
    """Dialog for adding/updating a customer."""

    def __init__(self, parent=None, customer_data: dict | None = None) -> None:
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
        self.contact_input = QLineEdit(self)  # Changed from mobile_input
        self.email_input = QLineEdit(self)
        self.address_input = QLineEdit(self)

        # Add fields to form
        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow(
            "Contact:", self.contact_input
        )  # Updated label
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Address:", self.address_input)

        # Add OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def validate(self) -> None:
        """Validate form inputs using CustomerBase model."""
        data = self.get_data()
        try:
            # Remove None values for validation
            cleaned_data = {k: v for k, v in data.items() if v is not None}
            CustomerBase(**cleaned_data)

            # Additional validation for required fields
            if not cleaned_data.get("name") or not cleaned_data.get(
                "contact_no"
            ):
                raise ValidationError(
                    [
                        {
                            "loc": ("name",),
                            "msg": "Name and contact number are required fields",
                        }
                    ]
                )

            self.accept()
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = error["loc"][0]
                message = error["msg"]
                error_messages.append(f"{field.title()}: {message}")

            QMessageBox.warning(
                self,
                "Validation Error",
                "Please correct the following errors:\n\n"
                + "\n".join(error_messages),
            )

    def set_data(self, customer_data: dict) -> None:
        """Set the dialog's fields with existing customer data."""
        self.name_input.setText(customer_data.get("name", ""))
        self.contact_input.setText(
            customer_data.get("contact_no", "")
        )  # Updated field name
        self.email_input.setText(customer_data.get("email", ""))
        self.address_input.setText(customer_data.get("address", ""))

    def get_data(self) -> dict:
        """Get the data from the dialog."""
        data = {
            "name": self.name_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
        }

        # Additional data cleaning
        if data["email"] == "":
            data["email"] = None
        if data["address"] == "":
            data["address"] = None

        return data


class CustomerGUI(QWidget):
    """Customer GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Customer GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.current_page = 1
        self.page_size = 15
        self.customer_view = CustomerView(model=Customer)

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
        self.search_criteria.addItems(
            ["Name", "Contact", "Email", "Address"]
        )  # Updated Mobile to Contact
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
        """Filter customers based on search criteria."""
        self.current_page = 1  # Reset to first page
        self.load_customers(refresh_all=False)

    def load_customers(self, refresh_all=True) -> None:
        """Load customers using backend pagination from BaseView."""
        try:
            search_text = self.search_input.text().lower()
            search_field = (
                self.search_criteria.currentText().lower()
                if search_text
                else None
            )

            with get_session() as session:
                # This uses BaseView's read_all implementation
                result = self.customer_view.read_all(
                    db_session=session,
                    page=self.current_page,
                    limit=self.page_size,
                    search_by=search_field,
                    search_query=search_text,
                )

                # Use PaginationBase attributes from base/model.py
                self.prev_button.setEnabled(
                    result.previous_record_id is not None
                )
                self.next_button.setEnabled(result.next_record_id is not None)

                self._update_table_data(result.records)
                self.update_pagination_buttons(result.total_pages)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        # Clear existing buttons
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_page = self.current_page

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

    def next_page(self) -> None:
        """Load the next page of customers."""
        self.current_page += 1
        self.load_customers(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of customers."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_customers(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if page_number != self.current_page:
            self.current_page = page_number
            self.load_customers(refresh_all=False)

    def _update_table_data(self, records: list) -> None:
        """Update table data with provided records."""
        self.customer_table.setRowCount(len(records) + 1)  # +1 for header
        self.customer_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Name", "Contact", "Email", "Address"]
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
                row, 2, QTableWidgetItem(customer.contact_no)
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(customer.email or "")
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(customer.address or "")
            )

        # Maintain table appearance
        self.customer_table.resizeColumnsToContents()
        self.customer_table.horizontalHeader().setStretchLastSection(True)

        # Set consistent row heights
        row_height = 40
        for row in range(self.customer_table.rowCount()):
            self.customer_table.setRowHeight(row, row_height)

    def add_customer(self) -> None:
        """Add customer using BaseView's create method."""
        try:
            dialog = CustomerDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                with get_session() as session:
                    # Uses BaseView's create method
                    new_customer = Customer(**dialog.get_data())
                    self.customer_view.create(
                        db_session=session, record=new_customer
                    )
                    self.load_customers(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Customer added successfully!"
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add customer: {e!s}"
            )

    def update_customer(self) -> None:
        """Update customer using BaseView's update_by_id method."""
        try:
            selected_row = self.customer_table.currentRow()
            if selected_row <= 0:
                return

            customer_id = int(self.customer_table.item(selected_row, 0).text())

            with get_session() as session:
                # Uses BaseView's read_by_id method
                customer = self.customer_view.read_by_id(
                    db_session=session, record_id=customer_id
                )
                if not customer:
                    QMessageBox.warning(
                        self, "Not Found", "Customer no longer exists"
                    )
                    return

                dialog = CustomerDialog(self)
                dialog.set_data(
                    {
                        "name": customer.name,
                        "contact_no": customer.contact_no,
                        "email": customer.email,
                        "address": customer.address,
                    }
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # Uses BaseView's update_by_id method
                    updated_customer = Customer(**dialog.get_data())
                    self.customer_view.update_by_id(
                        db_session=session,
                        record_id=customer_id,
                        record=updated_customer,
                    )
                    self.load_customers(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Customer updated successfully!"
                    )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update customer: {e!s}"
            )

    def delete_customer(self) -> None:
        """Delete customer using BaseView's delete_by_id method."""
        try:
            selected_row = self.customer_table.currentRow()
            if selected_row <= 0:
                return

            customer_id = int(self.customer_table.item(selected_row, 0).text())

            if (
                QMessageBox.question(
                    self,
                    "Confirm Delete",
                    "Are you sure you want to delete this customer?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                with get_session() as session:
                    # Uses BaseView's delete_by_id method
                    if self.customer_view.delete_by_id(
                        db_session=session, record_id=customer_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Customer deleted successfully!"
                        )
                        self.load_customers()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Customer not found!"
                        )

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
