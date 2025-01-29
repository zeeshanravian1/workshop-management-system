"""Customer GUI Module.

Description:
- This module provides the GUI for managing customers.

"""

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# from sqlalchemy.orm import Session
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


class CustomerGUI(QMainWindow):
    """Customer GUI Class.

    Description:
    - This class provides the GUI for managing customers.

    """

    def __init__(self):
        """Initialize the Customer GUI."""
        super().__init__()
        self.setWindowTitle("Customer Management")
        self.setGeometry(100, 100, 800, 600)

        self.customer_view = CustomerView(
            model=Customer
        )  # Initialize CustomerView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setSelectionBehavior(
            self.customer_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.customer_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Customers")
        self.load_button.clicked.connect(self.load_customers)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Customer")
        self.add_button.clicked.connect(self.add_customer)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Customer")
        self.update_button.clicked.connect(self.update_customer)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Customer")
        self.delete_button.clicked.connect(self.delete_customer)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_customers()  # Load customers on initialization

    def load_customers(self):
        """Load customers from the database and display them in the table."""
        try:
            with Session(engine) as session:
                customers = self.customer_view.read_all(db_session=session)
                self.customer_table.setRowCount(len(customers))
                self.customer_table.setColumnCount(6)
                self.customer_table.setHorizontalHeaderLabels(
                    [
                        "Name",
                        "Mobile",
                        "Email",
                        "Address",
                        "Vehicle Registration",
                    ]
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
                    self.customer_table.setItem(
                        row,
                        5,
                        QTableWidgetItem(customer.vehicle_registration_number),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load customers: {e!s}"
            )

    def add_customer(self):
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

            vehicle_reg, ok = QInputDialog.getText(
                self, "Add Customer", "Enter Vehicle Registration Number:"
            )
            if not ok or not vehicle_reg:
                return

            with Session(engine) as session:
                new_customer = Customer(
                    name=name,
                    mobile_number=mobile,
                    email=email,
                    address=address,
                    vehicle_registration_number=vehicle_reg,
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

    def update_customer(self):
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
            customer_id = item.text()

            # Get updated details from user
            name, ok = QInputDialog.getText(
                self, "Update Customer", "Enter New Name:"
            )
            if not ok or not name:
                return

            mobile, ok = QInputDialog.getText(
                self, "Update Customer", "Enter New Mobile Number:"
            )
            if not ok or not mobile:
                return

            email, ok = QInputDialog.getText(
                self, "Update Customer", "Enter New Email Address:"
            )
            if not ok or not email:
                return

            address, ok = QInputDialog.getText(
                self, "Update Customer", "Enter New Address:"
            )
            if not ok or not address:
                return

            vehicle_reg, ok = QInputDialog.getText(
                self,
                "Update Customer",
                "Enter New Vehicle Registration Number:",
            )
            if not ok or not vehicle_reg:
                return

            with Session(engine) as session:
                customer_obj = self.customer_view.read_by_id(
                    db_session=session, record_id=int(customer_id)
                )
                if customer_obj:
                    customer_obj.name = name
                    customer_obj.mobile_number = mobile
                    customer_obj.email = email
                    customer_obj.address = address
                    customer_obj.vehicle_registration_number = vehicle_reg
                    self.customer_view.update(
                        db_session=session,
                        record_id=int(customer_id),
                        record=customer_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Customer updated successfully!"
                    )
                    self.load_customers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update customer: {e!s}"
            )

    def delete_customer(self):
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
