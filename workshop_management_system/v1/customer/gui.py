"""Customer GUI Module.

Description:
- This module provides the GUI for managing customers.

"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


class CustomerGUI(QMainWindow):
    """Customer GUI Class."""

    def __init__(self) -> None:
        """Initialize the Customer GUI."""
        super().__init__()
        self.setWindowTitle("Customer Management")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
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
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                background-color: white;
            }
            QLabel {
                color: #333;
            }
        """)

        self.customer_view = CustomerView(model=Customer)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Customer Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Table Frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)

        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_table.setAlternatingRowColors(True)
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

    def load_customers(self) -> None:
        """Load customers from the database."""
        try:
            with Session(engine) as session:
                customers = self.customer_view.read_all(db_session=session)
                self.customer_table.setRowCount(len(customers))
                self.customer_table.setColumnCount(
                    5
                )  # ID, Name, Mobile, Email, Address
                self.customer_table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Mobile", "Email", "Address"]
                )

                for row, customer in enumerate(customers):
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
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def add_customer(self) -> None:
        """Add a new customer to the database."""
        try:
            # Get customer details from user
            name, ok = QInputDialog.getText(
                self, "Add Customer", "Enter Customer Name:"
            )
            if not ok or not name:
                return

            mobile, ok = QInputDialog.getText(
                self, "Add Customer", "Enter Mobile Number:"
            )
            if not ok or not mobile:
                return

            email, ok = QInputDialog.getText(
                self, "Add Customer", "Enter Email Address:"
            )
            if not ok or not email:
                return

            address, ok = QInputDialog.getText(
                self, "Add Customer", "Enter Address:"
            )
            if not ok or not address:
                return

            with Session(engine) as session:
                new_customer = Customer(
                    name=name,
                    mobile_number=mobile,
                    email=email,
                    address=address,
                )
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

            # Get updated details
            fields = {
                "Name": "name",
                "Mobile Number": "mobile_number",
                "Email": "email",
                "Address": "address",
            }

            new_values = {}
            for label, field in fields.items():
                value, ok = QInputDialog.getText(
                    self, "Update Customer", f"Enter New {label}:"
                )
                if not ok:
                    return
                new_values[field] = value

            with Session(engine) as session:
                customer = self.customer_view.read_by_id(
                    db_session=session, record_id=customer_id
                )
                if customer:
                    for field, value in new_values.items():
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


if __name__ == "__main__":
    app = QApplication([])
    window = CustomerGUI()
    window.show()
    app.exec()
