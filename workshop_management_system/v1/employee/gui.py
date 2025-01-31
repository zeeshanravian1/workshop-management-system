"""Employee GUI Module.

Description:
- This module provides the GUI for managing employees.

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
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.employee.model import Employee
from workshop_management_system.v1.employee.view import EmployeeView


class EmployeeGUI(QMainWindow):
    """Employee GUI Class.

    Description:
    - This class provides the GUI for managing employees.

    """

    def __init__(self) -> None:
        """Initialize the Employee GUI."""
        super().__init__()
        self.setWindowTitle("Employee Management")
        self.setGeometry(100, 100, 800, 600)

        self.employee_view = EmployeeView(
            model=Employee
        )  # Initialize EmployeeView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setSelectionBehavior(
            self.employee_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.employee_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Employees")
        self.load_button.clicked.connect(self.load_employees)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Employee")
        self.add_button.clicked.connect(self.add_employee)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Employee")
        self.update_button.clicked.connect(self.update_employee)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Employee")
        self.delete_button.clicked.connect(self.delete_employee)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_employees()  # Load employees on initialization

    def load_employees(self):
        """Load employees from the database and display them in the table."""
        try:
            with Session(engine) as session:
                employees = self.employee_view.read_all(db_session=session)
                self.employee_table.setRowCount(len(employees))
                self.employee_table.setColumnCount(6)
                self.employee_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Name",
                        "Username",
                        "Email",
                        "Role",
                        "Active",
                    ]
                )

                for row, employee in enumerate(employees):
                    self.employee_table.setItem(
                        row, 0, QTableWidgetItem(str(employee.id))
                    )
                    self.employee_table.setItem(
                        row, 1, QTableWidgetItem(employee.name)
                    )
                    self.employee_table.setItem(
                        row, 2, QTableWidgetItem(employee.username)
                    )
                    self.employee_table.setItem(
                        row, 3, QTableWidgetItem(employee.email)
                    )
                    self.employee_table.setItem(
                        row, 4, QTableWidgetItem(employee.role)
                    )
                    self.employee_table.setItem(
                        row, 5, QTableWidgetItem(str(employee.is_active))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load employees: {e!s}"
            )

    def add_employee(self):
        """Add a new employee to the database."""
        try:
            # Get employee details from user
            name, ok = QInputDialog.getText(
                self, "Add Employee", "Enter Employee Name:"
            )
            if not ok or not name:
                return

            username, ok = QInputDialog.getText(
                self, "Add Employee", "Enter Username:"
            )
            if not ok or not username:
                return

            email, ok = QInputDialog.getText(
                self, "Add Employee", "Enter Email Address:"
            )
            if not ok or not email:
                return

            password, ok = QInputDialog.getText(
                self, "Add Employee", "Enter Password:"
            )
            if not ok or not password:
                return

            role, ok = QInputDialog.getText(
                self, "Add Employee", "Enter Role:"
            )
            if not ok or not role:
                return

            with Session(engine) as session:
                new_employee = Employee(
                    name=name,
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                )
                self.employee_view.create(
                    db_session=session, record=new_employee
                )
                QMessageBox.information(
                    self, "Success", "Employee added successfully!"
                )
                self.load_employees()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add employee: {e!s}"
            )

    def update_employee(self):
        """Update an existing employee."""
        try:
            selected_row = self.employee_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an employee to update."
                )
                return

            item = self.employee_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected employee ID is invalid."
                )
                return
            employee_id = item.text()

            # Get updated details from user
            name, ok = QInputDialog.getText(
                self, "Update Employee", "Enter New Name:"
            )
            if not ok or not name:
                return

            username, ok = QInputDialog.getText(
                self, "Update Employee", "Enter New Username:"
            )
            if not ok or not username:
                return

            email, ok = QInputDialog.getText(
                self, "Update Employee", "Enter New Email Address:"
            )
            if not ok or not email:
                return

            password, ok = QInputDialog.getText(
                self, "Update Employee", "Enter New Password:"
            )
            if not ok or not password:
                return

            role, ok = QInputDialog.getText(
                self, "Update Employee", "Enter New Role:"
            )
            if not ok or not role:
                return

            with Session(engine) as session:
                employee_obj = self.employee_view.read_by_id(
                    db_session=session, record_id=int(employee_id)
                )
                if employee_obj:
                    employee_obj.name = name
                    employee_obj.username = username
                    employee_obj.email = email
                    employee_obj.password = password
                    employee_obj.role = role
                    self.employee_view.update(
                        db_session=session,
                        record_id=int(employee_id),
                        record=employee_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Employee updated successfully!"
                    )
                    self.load_employees()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update employee: {e!s}"
            )

    def delete_employee(self):
        """Delete an employee from the database."""
        try:
            selected_row = self.employee_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an employee to delete."
                )
                return

            item = self.employee_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected employee ID is invalid."
                )
                return
            employee_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Employee",
                "Are you sure you want to delete this employee?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.employee_view.delete(
                        db_session=session, record_id=int(employee_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Employee deleted successfully!"
                    )
                    self.load_employees()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete employee: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = EmployeeGUI()
    window.show()
    app.exec()
