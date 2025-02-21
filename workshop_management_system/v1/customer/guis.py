import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


# Embedded: Dialog for adding a new customer.
class CustomerDialog(QDialog):
    """Dialog to add a new customer."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.address_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Contact No:", self.contact_input)
        layout.addRow("Address:", self.address_input)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "address": self.address_input.text().strip(),
        }


# Embedded: Dialog for updating an existing customer.
class CustomerUpdateDialog(QDialog):
    """Dialog to update an existing customer."""

    def __init__(self, initial_data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Update Customer")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.name_input = QLineEdit(initial_data.get("Name", ""))
        self.email_input = QLineEdit(initial_data.get("Email", ""))
        self.contact_input = QLineEdit(initial_data.get("Contact No", ""))
        self.address_input = QLineEdit(initial_data.get("Address", ""))
        layout.addRow("Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Contact No:", self.contact_input)
        layout.addRow("Address:", self.address_input)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "contact_no": self.contact_input.text().strip(),
            "address": self.address_input.text().strip(),
        }


class CustomerGUI(BaseGUI):
    """Customer GUI Class."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        header = QLabel(
            "Customer Management", alignment=Qt.AlignmentFlag.AlignCenter
        )
        header.setObjectName("headerLabel")
        self.layout().insertWidget(0, header)
        self.customer_view = CustomerView(Customer)
        self.all_items = self.load_customers()
        self.filtered_items = self.all_items.copy()
        self.load_items()

    def get_search_criteria(self) -> list[str]:
        return ["ID", "Name", "Email", "Contact No", "Address"]

    def load_customers(self) -> list[dict]:
        # Placeholder data based on customer/model.py fields.
        return [
            {
                "ID": 1,
                "Name": "Alice Smith",
                "Email": "alice@example.com",
                "Contact No": "+123456789",
                "Address": "123 Main St",
            },
            {
                "ID": 2,
                "Name": "Bob Johnson",
                "Email": "bob@example.com",
                "Contact No": "+987654321",
                "Address": "456 Market Ave",
            },
        ]

    def load_items(self) -> None:
        self.customer_table.setRowCount(
            len(self.filtered_items) + 1
        )  # +1 for header
        self.customer_table.setColumnCount(5)
        headers = ["ID", "Name", "Email", "Contact No", "Address"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)
        for row, data in enumerate(self.filtered_items, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(data["ID"]))
            )
            self.customer_table.setItem(row, 1, QTableWidgetItem(data["Name"]))
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(data["Email"])
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(data["Contact No"])
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(data["Address"])
            )

    def add_customer(self) -> None:
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            QMessageBox.information(
                self,
                "Customer Data",
                f"Name: {data['name']}\nEmail: {data['email']}\n"
                f"Contact No: {data['contact_no']}\nAddress: {data['address']}",
            )

    def update_customer(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row < 1:
            QMessageBox.warning(
                self, "Update", "Please select a customer to update."
            )
            return
        current_data = {
            "Name": self.customer_table.item(selected_row, 1).text(),
            "Email": self.customer_table.item(selected_row, 2).text(),
            "Contact No": self.customer_table.item(selected_row, 3).text(),
            "Address": self.customer_table.item(selected_row, 4).text(),
        }
        dialog = CustomerUpdateDialog(initial_data=current_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            QMessageBox.information(
                self,
                "Updated Customer Data",
                f"Name: {updated_data['name']}\nEmail: {updated_data['email']}\n"
                f"Contact No: {updated_data['contact_no']}\nAddress: {updated_data['address']}",
            )

    def delete_customer(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row >= 1:
            QMessageBox.information(
                self, "Delete", "Delete customer functionality"
            )

    def add(self) -> None:
        self.add_customer()

    def show_context_menu(self, position) -> None:
        row = self.customer_table.rowAt(position.y())
        if row >= 0:
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            self.apply_styles(context_menu)
            update_action = context_menu.addAction("✏️  Update")
            update_action.setStatusTip("Update selected customer")
            context_menu.addSeparator()
            delete_action = context_menu.addAction("🗑️  Delete")
            delete_action.setStatusTip("Delete selected customer")
            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_customer()
            elif action == delete_action:
                self.delete_customer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    customer_gui = CustomerGUI(main_window)
    main_window.setCentralWidget(customer_gui)
    main_window.setWindowTitle("Customer Management System")
    main_window.resize(800, 600)
    customer_gui.apply_styles(main_window)
    customer_gui.apply_styles()
    main_window.show()
    sys.exit(app.exec())
