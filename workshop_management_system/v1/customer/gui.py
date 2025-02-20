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
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from workshop_management_system.database.session import get_session
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


"""Customer Dialog for managing customer details."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)
from pydantic import ValidationError

from workshop_management_system.v1.customer.model import CustomerBase


class CustomerDialog(QDialog):
    """Dialog for adding/updating a customer."""

    def __init__(
        self, parent: QWidget | None = None, customer_data: dict | None = None
    ) -> None:
        """Initialize the customer dialog.

        Args:
            parent: The parent widget.
            customer_data: Dictionary containing customer information.
        """
        super().__init__(parent)
        self.setWindowTitle("Customer Details")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #f0f0f0; }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QFormLayout { spacing: 15px; }
        """)

        layout = QFormLayout(self)

        # Input fields
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()

        # Add fields to form
        layout.addRow("Name:", self.name_input)
        layout.addRow("Contact:", self.contact_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Address:", self.address_input)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        # Set data if provided
        if customer_data:
            self.name_input.setText(customer_data.get("name", ""))
            self.contact_input.setText(customer_data.get("contact_no", ""))
            self.email_input.setText(customer_data.get("email", ""))
            self.address_input.setText(customer_data.get("address", ""))

    def validate(self) -> None:
        """Validate form inputs using CustomerBase model validation."""
        data = self.get_data()

        try:
            # Use CustomerBase for validation
            CustomerBase(
                name=data["name"],
                contact_no=data["contact_no"],
                email=data["email"],
                address=data["address"],
            )
            self.accept()

        except ValidationError as e:
            # Format validation errors for display
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

    def get_data(self) -> dict:
        """Get form data as dictionary."""
        return {
            "name": self.name_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
        }

    def validate(self) -> None:
        """Validate form inputs before accepting."""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required!")
            return
        if not self.contact_input.hasAcceptableInput():
            QMessageBox.warning(
                self, "Validation Error", "Invalid contact number!"
            )
            return
        if (
            self.email_input.text()
            and not self.email_input.hasAcceptableInput()
        ):
            QMessageBox.warning(
                self, "Validation Error", "Invalid email format!"
            )
            return
        self.accept()

    def get_data(self) -> dict:
        """Get form data as dictionary."""
        return {
            "name": self.name_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
        }


class CustomerGUI(QWidget):
    """Customer management GUI."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.customer_view = CustomerView(model=Customer)
        self.current_page = 1
        self.page_size = 25

        self._setup_ui()
        self._load_customers()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.setStyleSheet("""
            QWidget { background-color: white; color: black; }
            QPushButton {
                padding: 10px;
                background-color: skyblue;
                color: black;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover { background-color: #ADD8E6; }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("Customer Management")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_field = QComboBox()
        self.search_field.addItems(["name", "email", "contact_no", "address"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.textChanged.connect(self._load_customers)
        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Buttons
        button_layout = QHBoxLayout()
        home_btn = QPushButton("Home")
        home_btn.clicked.connect(
            lambda: self.parent_widget.back_to_home()
            if self.parent_widget
            else None
        )
        add_btn = QPushButton("Add Customer")
        add_btn.clicked.connect(self._handle_add_customer)
        button_layout.addWidget(home_btn)
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
            }
        """)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

        # Pagination
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(lambda: self._change_page(-1))
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(lambda: self._change_page(1))
        self.page_label = QLabel()
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

    def _add_customer(self, customer: Customer) -> None:
        """Add customer to table."""
        data = CustomerDialog.get_data(customer)
        row = self.table.rowCount()

    def _load_customers(self) -> None:
        """Load customers using the customer view."""
        try:
            with get_session() as session:
                search_query = self.search_input.text()
                search_field = (
                    self.search_field.currentText() if search_query else None
                )

                result = self.customer_view.read_all(
                    db_session=session,
                    page=self.current_page,
                    limit=self.page_size,
                    search_by=search_field,
                    search_query=search_query,
                )

                # Update pagination controls
                self.prev_btn.setEnabled(result.previous_record_id is not None)
                self.next_btn.setEnabled(result.next_record_id is not None)
                self.page_label.setText(
                    f"Page {result.current_page} of {result.total_pages}"
                )

                # Update table
                self.table.setRowCount(
                    len(result.records) + 1
                )  # +1 for header
                self.table.setColumnCount(5)

                # Set headers
                headers = ["ID", "Name", "Contact", "Email", "Address"]
                for col, header in enumerate(headers):
                    item = QTableWidgetItem(header)
                    item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                    self.table.setItem(0, col, item)

                # Set data
                for row, customer in enumerate(result.records, 1):
                    self.table.setItem(
                        row, 0, QTableWidgetItem(str(customer.id))
                    )
                    self.table.setItem(row, 1, QTableWidgetItem(customer.name))
                    self.table.setItem(
                        row, 2, QTableWidgetItem(customer.contact_no)
                    )
                    self.table.setItem(
                        row, 3, QTableWidgetItem(customer.email or "")
                    )
                    self.table.setItem(
                        row, 4, QTableWidgetItem(customer.address or "")
                    )

                self.table.resizeColumnsToContents()
                self.table.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def _handle_add_customer(self) -> None:
        """Handle add customer action."""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                with get_session() as session:
                    new_customer = Customer(**dialog.get_data())
                    self.customer_view.create(
                        db_session=session, record=new_customer
                    )
                    QMessageBox.information(
                        self, "Success", "Customer added successfully!"
                    )
                    self._load_customers()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add customer: {e!s}"
                )

    def _handle_update_customer(self, customer_id: int) -> None:
        """Handle update customer action."""
        try:
            with get_session() as session:
                customer = self.customer_view.read_by_id(
                    db_session=session, record_id=customer_id
                )
                if not customer:
                    return

                dialog = CustomerDialog(
                    self,
                    {
                        "name": customer.name,
                        "contact_no": customer.contact_no,
                        "email": customer.email,
                        "address": customer.address,
                    },
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_customer = Customer(**dialog.get_data())
                    self.customer_view.update_by_id(
                        db_session=session,
                        record_id=customer_id,
                        record=updated_customer,
                    )
                    QMessageBox.information(
                        self, "Success", "Customer updated successfully!"
                    )
                    self._load_customers()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update customer: {e!s}"
            )

    def _handle_delete_customer(self, customer_id: int) -> None:
        """Handle delete customer action."""
        try:
            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this customer?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                with get_session() as session:
                    if self.customer_view.delete_by_id(
                        db_session=session, record_id=customer_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Customer deleted successfully!"
                        )
                        self._load_customers()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Customer not found!"
                        )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete customer: {e!s}"
            )

    def _show_context_menu(self, position) -> None:
        """Show context menu for table row."""
        row = self.table.rowAt(position.y())
        if row <= 0:  # Skip header row
            return

        self.table.selectRow(row)
        customer_id = int(self.table.item(row, 0).text())

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                color: black;
            }
            QMenu::item:selected {
                background-color: #e6f3ff;
            }
        """)

        update_action = menu.addAction("✏️ Update")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Delete")

        action = menu.exec(self.table.mapToGlobal(position))
        if action == update_action:
            self._handle_update_customer(customer_id)
        elif action == delete_action:
            self._handle_delete_customer(customer_id)

    def _change_page(self, delta: int) -> None:
        """Change the current page by delta."""
        self.current_page += delta
        self._load_customers()


if __name__ == "__main__":
    app = QApplication([])
    window = CustomerGUI()
    window.show()
    app.exec()
