"""Service GUI Module.

Description:
- This module provides the GUI for managing services.

"""

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.employee.model import Employee
from workshop_management_system.v1.service.model import Service
from workshop_management_system.v1.service.view import ServiceView


class ServiceGUI(QMainWindow):
    """Service GUI Class.

    Description:
    - This class provides the GUI for managing services.

    """

    def __init__(self) -> None:
        """Initialize the Service GUI."""
        super().__init__()
        self.setWindowTitle("Service Management")
        self.setGeometry(100, 100, 800, 600)

        self.service_view = ServiceView(
            model=Service
        )  # Initialize ServiceView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Service table
        self.service_table = QTableWidget()
        self.service_table.setSelectionBehavior(
            self.service_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.service_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Services")
        self.load_button.clicked.connect(self.load_services)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Service")
        self.add_button.clicked.connect(self.add_service)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Service")
        self.update_button.clicked.connect(self.update_service)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Service")
        self.delete_button.clicked.connect(self.delete_service)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_services()  # Load services on initialization

    def load_services(self) -> None:
        """Load services from the database and display them in the table."""
        try:
            with Session(engine) as session:
                services = self.service_view.read_all(db_session=session)
                self.service_table.setRowCount(len(services))
                self.service_table.setColumnCount(6)
                self.service_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Job Card ID",
                        "Employee Name",
                        "Service Type",
                        "Description",
                        "Cost",
                    ]
                )

                for row, service in enumerate(services):
                    employee = session.exec(
                        select(Employee).where(
                            Employee.id == service.employee_id
                        )
                    ).first()
                    self.service_table.setItem(
                        row, 0, QTableWidgetItem(str(service.id))
                    )
                    self.service_table.setItem(
                        row, 1, QTableWidgetItem(str(service.job_card_id))
                    )
                    self.service_table.setItem(
                        row,
                        2,
                        QTableWidgetItem(employee.name if employee else ""),
                    )
                    self.service_table.setItem(
                        row, 3, QTableWidgetItem(service.service_type)
                    )
                    self.service_table.setItem(
                        row, 4, QTableWidgetItem(service.description)
                    )
                    self.service_table.setItem(
                        row, 5, QTableWidgetItem(str(service.cost))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load services: {e!s}"
            )

    def add_service(self) -> None:
        """Add a new service to the database."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Service")
            layout = QFormLayout(dialog)

            job_card_id_input = QLineEdit(dialog)
            employee_name_input = QLineEdit(dialog)
            service_type_input = QLineEdit(dialog)
            description_input = QLineEdit(dialog)
            cost_input = QLineEdit(dialog)

            layout.addRow("Job Card ID:", job_card_id_input)
            layout.addRow("Employee Name:", employee_name_input)
            layout.addRow("Service Type:", service_type_input)
            layout.addRow("Description:", description_input)
            layout.addRow("Cost:", cost_input)

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel,
                dialog,
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                job_card_id = int(job_card_id_input.text())
                employee_name = employee_name_input.text()
                service_type = service_type_input.text()
                description = description_input.text()
                cost = float(cost_input.text())

                with Session(engine) as session:
                    employee = session.exec(
                        select(Employee).where(Employee.name == employee_name)
                    ).first()
                    if not employee:
                        QMessageBox.critical(
                            self, "Error", "Employee not found."
                        )
                        return

                    new_service = Service(
                        job_card_id=job_card_id,
                        employee_id=employee.id,
                        service_type=service_type,
                        description=description,
                        cost=cost,
                    )
                    self.service_view.create(
                        db_session=session, record=new_service
                    )
                    QMessageBox.information(
                        self, "Success", "Service added successfully!"
                    )
                    self.load_services()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add service: {e!s}"
            )

    def update_service(self) -> None:
        """Update an existing service."""
        try:
            selected_row = self.service_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service to update."
                )
                return

            item = self.service_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected service ID is invalid."
                )
                return
            service_id = item.text()

            dialog = QDialog(self)
            dialog.setWindowTitle("Update Service")
            layout = QFormLayout(dialog)

            job_card_id_input = QLineEdit(dialog)
            employee_name_input = QLineEdit(dialog)
            service_type_input = QLineEdit(dialog)
            description_input = QLineEdit(dialog)
            cost_input = QLineEdit(dialog)

            layout.addRow("Job Card ID:", job_card_id_input)
            layout.addRow("Employee Name:", employee_name_input)
            layout.addRow("Service Type:", service_type_input)
            layout.addRow("Description:", description_input)
            layout.addRow("Cost:", cost_input)

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel,
                dialog,
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                job_card_id = int(job_card_id_input.text())
                employee_name = employee_name_input.text()
                service_type = service_type_input.text()
                description = description_input.text()
                cost = float(cost_input.text())

                with Session(engine) as session:
                    service_obj = self.service_view.read_by_id(
                        db_session=session, record_id=int(service_id)
                    )
                    if service_obj:
                        employee = session.exec(
                            select(Employee).where(
                                Employee.name == employee_name
                            )
                        ).first()
                        if not employee:
                            QMessageBox.critical(
                                self, "Error", "Employee not found."
                            )
                            return

                        service_obj.job_card_id = job_card_id
                        service_obj.employee_id = employee.id
                        service_obj.service_type = service_type
                        service_obj.description = description
                        service_obj.cost = cost
                        self.service_view.update(
                            db_session=session,
                            record_id=int(service_id),
                            record=service_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Service updated successfully!"
                        )
                        self.load_services()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update service: {e!s}"
            )

    def delete_service(self) -> None:
        """Delete a service from the database."""
        try:
            selected_row = self.service_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service to delete."
                )
                return

            item = self.service_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected service ID is invalid."
                )
                return
            service_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Service",
                "Are you sure you want to delete this service?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.service_view.delete(
                        db_session=session, record_id=int(service_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Service deleted successfully!"
                    )
                    self.load_services()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete service: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = ServiceGUI()
    window.show()
    app.exec()
