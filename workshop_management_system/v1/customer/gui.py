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
        # Add pagination properties
        self.page_size = 15  # Increased from 10 to 15
        self.current_page = 1
        self.total_records = 0
        self.all_customers = []  # Add this to store all customers
        self.filtered_customers = []  # Add this to store filtered results

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
        self.current_page = 1
        self.total_records = len(self.filtered_customers)

        # Reload the table with filtered data
        self.load_customers(refresh_all=False)

    def update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        # Clear existing buttons
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        max_visible_pages = 7
        if total_pages <= max_visible_pages:
            # Show all pages
            for page in range(1, total_pages + 1):
                self.add_page_button(page)
        else:
            # Show first pages
            for page in range(1, 4):
                self.add_page_button(page)

            # Add ellipsis
            if self.current_page > 4:
                ellipsis = QPushButton("...")
                ellipsis.setEnabled(False)
                ellipsis.setStyleSheet("background: none; border: none;")
                self.page_buttons_layout.addWidget(ellipsis)

            # Show current and surrounding pages
            if 4 < self.current_page < total_pages - 3:
                self.add_page_button(self.current_page)

            # Add ending ellipsis
            if self.current_page < total_pages - 3:
                ellipsis = QPushButton("...")
                ellipsis.setEnabled(False)
                ellipsis.setStyleSheet("background: none; border: none;")
                self.page_buttons_layout.addWidget(ellipsis)

            # Show last pages
            for page in range(total_pages - 2, total_pages + 1):
                self.add_page_button(page)

    def add_page_button(self, page_num: int) -> None:
        """Add a single page button."""
        button = QPushButton(str(page_num))
        button.setFixedSize(40, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if page_num == self.current_page:
            button.setStyleSheet("""
                QPushButton {
                    background-color: skyblue;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                    border-radius: 20px;
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
                    self.total_records = len(self.all_customers)

                total_pages = (
                    self.total_records + self.page_size - 1
                ) // self.page_size

                # Calculate offset
                offset = (self.current_page - 1) * self.page_size

                # Get paginated customers from filtered results
                current_page_customers = self.filtered_customers[
                    offset : offset + self.page_size
                ]

                # Set up table
                self.customer_table.setRowCount(
                    len(current_page_customers) + 1
                )
                self.customer_table.setColumnCount(5)

                # Update table contents
                # Set column headers
                column_names = ["ID", "Name", "Mobile", "Email", "Address"]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.customer_table.setItem(0, col, item)

                # Populate table with current page data
                for row, customer in enumerate(
                    current_page_customers, start=1
                ):
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

                # Update pagination buttons
                self.update_pagination_buttons(total_pages)

                # Update navigation buttons
                self.prev_button.setEnabled(self.current_page > 1)
                self.next_button.setEnabled(self.current_page < total_pages)

                # Adjust table appearance
                self.customer_table.resizeColumnsToContents()
                self.customer_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.customer_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )

                # Calculate row height based on content
                row_height = 40  # Default height
                visible_rows = min(
                    len(current_page_customers) + 1, self.page_size + 1
                )

                # Set fixed row height
                for row in range(visible_rows):
                    self.customer_table.setRowHeight(row, row_height)

                # Set table height to accommodate only visible rows
                table_height = (row_height * visible_rows) + 20  # Add padding
                self.customer_table.setMinimumHeight(0)
                self.customer_table.setMaximumHeight(
                    16777215
                )  # Qt's maximum value

                # Update table appearance for better scrolling
                self.customer_table.setVerticalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )
                self.customer_table.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def next_page(self) -> None:
        """Load the next page of customers."""
        total_pages = (
            self.total_records + self.page_size - 1
        ) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_customers(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of customers."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_customers(refresh_all=False)

    def go_to_page(self, page_number):
        """Navigate to specific page number."""
        if page_number != self.current_page:
            self.current_page = page_number
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
