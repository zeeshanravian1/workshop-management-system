"""Customer GUI Module.

Description:
- This module provides the GUI for managing customers.

"""

from pydantic import ValidationError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.database.session import get_session
from workshop_management_system.v1.base.gui import (
    BaseDialog,
    BaseManagementGUI,
)
from workshop_management_system.v1.base.model import PaginationBase
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView


class CustomerDialog(BaseDialog):
    """Dialog for adding/updating a customer."""

    def __init__(self, parent=None, customer_data: dict | None = None) -> None:
        """Initialize the Customer Dialog."""
        super().__init__(parent, customer_data)
        self.setWindowTitle("Customer Details")

    def setup_form(self) -> None:
        """Setup the customer form fields."""
        self.name_input = QLineEdit(self)
        self.contact_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.address_input = QLineEdit(self)

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Contact:", self.contact_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Address:", self.address_input)

        if hasattr(self, "data") and self.data:
            self.set_data(self.data)

    def validate(self) -> None:
        """Validate form inputs using CustomerBase model."""
        data = self.get_data()
        try:
            cleaned_data = {k: v for k, v in data.items() if v is not None}
            CustomerBase(**cleaned_data)

            if not (
                cleaned_data.get("name") and cleaned_data.get("contact_no")
            ):  # Fixed line length
                raise ValidationError(
                    [
                        {
                            "loc": ("name",),
                            "msg": (
                                "Name and contact number are required fields"
                            ),
                        }
                    ]
                )

            self.accept()
        except ValidationError as e:
            error_messages: list[str] = [
                f"{error['loc'][0].title()}: {error['msg']}"
                for error in e.errors()
            ]
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please correct the following errors:\n\n"
                + "\n".join(error_messages),
            )

    def set_data(self, customer_data: dict) -> None:
        """Set the dialog's fields with existing customer data."""
        self.name_input.setText(customer_data.get("name", ""))
        self.contact_input.setText(customer_data.get("contact_no", ""))
        self.email_input.setText(customer_data.get("email", ""))
        self.address_input.setText(customer_data.get("address", ""))

    def get_data(self) -> dict:
        """Get the data from the dialog."""
        return {
            "name": self.name_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
        }


class CustomerGUI(BaseManagementGUI):
    """Customer GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Customer GUI."""
        self.customer_view = CustomerView(model=Customer)
        super().__init__(parent)

    def setup_header(self, main_layout) -> None:
        """Setup customer management header."""
        super().setup_header(main_layout)
        self.findChild(QLabel).setText("Customer Management")

    def setup_search(self, main_layout) -> None:
        """Setup customer search components."""
        super().setup_search(main_layout)
        self.search_input.setPlaceholderText("Search customers...")
        self.search_criteria.addItems(["Name", "Contact", "Email", "Address"])
        self.search_input.textChanged.connect(self.search_customers)
        self.search_criteria.currentTextChanged.connect(self.search_customers)

    def search_customers(self) -> None:
        """Filter customers based on search criteria."""
        self.current_page = 1
        self.load_records(refresh_all=False)

    def add_record(self) -> None:
        """Add a new customer record."""
        try:
            dialog = CustomerDialog(self)
            if dialog.exec() == CustomerDialog.DialogCode.Accepted:
                with get_session() as session:
                    new_customer = Customer(**dialog.get_data())
                    self.customer_view.create(
                        db_session=session, record=new_customer
                    )
                    self.load_records(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Customer added successfully!"
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add customer: {e!s}"
            )

    def update_record(self) -> None:
        """Update a customer record."""
        try:
            selected_row = self.table.currentRow()
            if selected_row <= 0:
                return

            customer_id = int(self.table.item(selected_row, 0).text())

            with get_session() as session:
                customer: Customer | None = self.customer_view.read_by_id(
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

                if dialog.exec() == CustomerDialog.DialogCode.Accepted:
                    updated_customer = Customer(**dialog.get_data())
                    self.customer_view.update_by_id(
                        db_session=session,
                        record_id=customer_id,
                        record=updated_customer,
                    )
                    self.load_records(refresh_all=True)
                    QMessageBox.information(
                        self, "Success", "Customer updated successfully!"
                    )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update customer: {e!s}"
            )

    def delete_record(self) -> None:
        """Delete a customer record."""
        try:
            selected_row = self.table.currentRow()
            if selected_row <= 0:
                return

            customer_id = int(self.table.item(selected_row, 0).text())

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
                    if self.customer_view.delete_by_id(
                        db_session=session, record_id=customer_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Customer deleted successfully!"
                        )
                        self.load_records()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Customer not found!"
                        )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete customer: {e!s}"
            )

    def load_records(self, refresh_all=True) -> None:
        """Load customers using backend pagination."""
        try:
            search_text = self.search_input.text().lower()
            search_field = (
                self.search_criteria.currentText().lower()
                if search_text
                else None
            )

            with get_session() as session:
                result: PaginationBase[Customer] = self.customer_view.read_all(
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
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def _update_table_data(self, records: list) -> None:
        """Update table data with provided records."""
        self.table.setRowCount(len(records) + 1)  # +1 for header
        self.table.setColumnCount(5)

        # Set headers
        headers: list[str] = ["ID", "Name", "Contact", "Email", "Address"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.table.setItem(0, col, item)

        # Populate data
        for row, customer in enumerate(records, start=1):
            self.table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
            self.table.setItem(row, 1, QTableWidgetItem(customer.name))
            self.table.setItem(row, 2, QTableWidgetItem(customer.contact_no))
            self.table.setItem(row, 3, QTableWidgetItem(customer.email or ""))
            self.table.setItem(
                row, 4, QTableWidgetItem(customer.address or "")
            )

        # Update table appearance
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)

    def show_context_menu(self, position) -> None:
        """Show context menu for table row."""
        row = self.table.rowAt(position.y())
        if row > 0:  # Skip header row
            self.table.selectRow(row)
            context_menu = QMenu(self)

            update_action = context_menu.addAction("✏️ Update")
            update_action.setStatusTip("Update selected customer")

            context_menu.addSeparator()

            delete_action = context_menu.addAction("🗑️ Delete")
            delete_action.setStatusTip("Delete selected customer")

            action = context_menu.exec(self.table.mapToGlobal(position))
            if action == update_action:
                self.update_record()
            elif action == delete_action:
                self.delete_record()


if __name__ == "__main__":
    app = QApplication([])
    window = CustomerGUI()
    window.show()
    app.exec()
