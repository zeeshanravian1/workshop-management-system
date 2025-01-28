"""Service GUI Module.

Description:
- This module provides the GUI for managing services.
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
from workshop_management_system.v1.service.model import Service
from workshop_management_system.v1.service.view import ServiceView


class ServiceGUI(QMainWindow):
    """Service GUI Class.

    Description:
    - This class provides the GUI for managing services.
    """

    def __init__(self):
        """Initialize the Service GUI."""
        super().__init__()
        self.setWindowTitle("Service Management")
        self.setGeometry(100, 100, 800, 600)

        self.service_view = ServiceView(model=Service)

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

        self.load_services()

    def load_services(self):
        """Load services from the database and display them in the table."""
        try:
            with Session(engine) as session:
                services = self.service_view.read_all(db_session=session)
                self.service_table.setRowCount(len(services))
                self.service_table.setColumnCount(5)
                self.service_table.setHorizontalHeaderLabels(
                    ["ID", "Job Card ID", "Service Type", "Description", "Cost"]
                )

                for row, service in enumerate(services):
                    self.service_table.setItem(
                        row, 0, QTableWidgetItem(str(service.id))
                    )
                    self.service_table.setItem(
                        row, 1, QTableWidgetItem(str(service.job_card_id))
                    )
                    self.service_table.setItem(
                        row, 2, QTableWidgetItem(service.service_type)
                    )
                    self.service_table.setItem(
                        row, 3, QTableWidgetItem(service.description)
                    )
                    self.service_table.setItem(
                        row, 4, QTableWidgetItem(str(service.cost))
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load services: {e!s}")

    def add_service(self):
        """Add a new service to the database."""
        try:
            job_card_id, ok = QInputDialog.getInt(
                self, "Add Service", "Enter Job Card ID:", 1, 1
            )
            if not ok:
                return

            service_type, ok = QInputDialog.getText(
                self, "Add Service", "Enter Service Type:"
            )
            if not ok or not service_type:
                return

            description, ok = QInputDialog.getText(
                self, "Add Service", "Enter Description:"
            )
            if not ok or not description:
                return

            cost, ok = QInputDialog.getDouble(
                self, "Add Service", "Enter Cost:", 0.0, 0.0, 1000000.0, 2
            )
            if not ok:
                return

            with Session(engine) as session:
                new_service = Service(
                    job_card_id=job_card_id,
                    service_type=service_type,
                    description=description,
                    cost=cost,
                )
                self.service_view.create(db_session=session, record=new_service)
                QMessageBox.information(
                    self, "Success", "Service added successfully!"
                )
                self.load_services()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add service: {e!s}")

    def update_service(self):
        """Update an existing service."""
        try:
            selected_row = self.service_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service to update."
                )
                return

            service_id = int(self.service_table.item(selected_row, 0).text())

            service_type, ok = QInputDialog.getText(
                self, "Update Service", "Enter New Service Type:"
            )
            if not ok or not service_type:
                return

            description, ok = QInputDialog.getText(
                self, "Update Service", "Enter New Description:"
            )
            if not ok or not description:
                return

            cost, ok = QInputDialog.getDouble(
                self, "Update Service", "Enter New Cost:", 0.0, 0.0, 1000000.0, 2
            )
            if not ok:
                return

            with Session(engine) as session:
                service_obj = self.service_view.read_by_id(
                    db_session=session, record_id=service_id
                )
                if service_obj:
                    service_obj.service_type = service_type
                    service_obj.description = description
                    service_obj.cost = cost
                    self.service_view.update(
                        db_session=session,
                        record_id=service_id,
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

    def delete_service(self):
        """Delete a service from the database."""
        try:
            selected_row = self.service_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service to delete."
                )
                return

            service_id = int(self.service_table.item(selected_row, 0).text())

            confirmation = QMessageBox.question(
                self,
                "Delete Service",
                "Are you sure you want to delete this service?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.service_view.delete(
                        db_session=session, record_id=service_id
                    )
                    QMessageBox.information(
                        self, "Success", "Service deleted successfully!"
                    )
                    self.load_services()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete service: {e!s}"
            )
