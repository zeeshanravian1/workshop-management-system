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
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #87CEEB;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                min-width: 125px;
                margin: 0px;
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #87CEEB;
                color: white;
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

        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_table.setAlternatingRowColors(False)  # Disable alternating colors
        self.customer_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.customer_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ddd;
            }
        """)
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.horizontalHeader().setVisible(False)
        self.customer_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.customer_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.customer_table.itemSelectionChanged.connect(self.on_row_selected)
        table_layout.addWidget(self.customer_table)
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
            ("Load Customers", self.load_customers),
            ("Add Customer", self.add_customer),
            ("Update Customer", self.update_customer),
            ("Delete Customer", self.delete_customer),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_customers()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def search_customers(self) -> None:
        """Filter customers based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.customer_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "name":
                    cell_text = self.customer_table.item(row, 1)
                elif criteria == "mobile":
                    cell_text = self.customer_table.item(row, 2)
                elif criteria == "email":
                    cell_text = self.customer_table.item(row, 3)
                elif criteria == "address":
                    cell_text = self.customer_table.item(row, 4)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.customer_table.setRowHidden(row, not show_row)

    def load_customers(self) -> None:
        """Load customers from the database."""
        try:
            with Session(engine) as session:
                customers = self.customer_view.read_all(db_session=session)
                self.customer_table.setRowCount(len(customers) + 1)
                self.customer_table.setColumnCount(
                    5
                )  # ID, Name, Mobile, Email, Address

                # Set column names in the first row
                column_names = ["ID", "Name", "Mobile", "Email", "Address"]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.customer_table.setItem(0, col, item)

                # Set the height of the first row
                self.customer_table.setRowHeight(0, 40)

                for row, customer in enumerate(customers, start=1):
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

                # Adjust column widths
                self.customer_table.resizeColumnsToContents()
                self.customer_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.customer_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )

                # After loading customers, apply any existing search filter
                self.search_customers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

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
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a customer to update."
                )
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
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a customer to delete."
                )
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
