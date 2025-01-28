"""Estimate GUI Module.

Description:
- This module provides the GUI for managing estimates.

"""

from datetime import datetime
from uuid import UUID

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
from workshop_management_system.v1.estimate.model import Estimate
from workshop_management_system.v1.estimate.view import EstimateView
from workshop_management_system.v1.vehicle.model import Vehicle


class EstimateDialog(QDialog):
    """Dialog for adding/updating an estimate."""

    def __init__(self, parent=None):
        """Intialize the Estimate Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Estimate Details")
        self.form_layout = QFormLayout(self)

        self.total_amount_input = QLineEdit(self)
        self.status_input = QLineEdit(self)
        self.description_input = QLineEdit(self)
        self.vehicle_id_input = QLineEdit(self)

        self.form_layout.addRow(
            "Total Estimate Amount:", self.total_amount_input
        )
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow(
            "Description (optional):", self.description_input
        )
        self.form_layout.addRow("Vehicle ID:", self.vehicle_id_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def get_data(self):
        """Get the data from the dialog."""
        return {
            "total_amount": float(self.total_amount_input.text()),
            "status": self.status_input.text(),
            "description": self.description_input.text(),
            "vehicle_id": self.vehicle_id_input.text(),
        }


class EstimateGUI(QMainWindow):
    """Estimate GUI Class.

    Description:
    - This class provides the GUI for managing estimates.

    """

    def __init__(self):
        """Initialize the Estimate GUI."""
        super().__init__()
        self.setWindowTitle("Estimate Management")
        self.setGeometry(100, 100, 800, 600)

        self.estimate_view = EstimateView(
            model=Estimate
        )  # Initialize EstimateView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Estimate table
        self.estimate_table = QTableWidget()
        self.estimate_table.setSelectionBehavior(
            self.estimate_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.estimate_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Estimates")
        self.load_button.clicked.connect(self.load_estimates)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Estimate")
        self.add_button.clicked.connect(self.add_estimate)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Estimate")
        self.update_button.clicked.connect(self.update_estimate)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Estimate")
        self.delete_button.clicked.connect(self.delete_estimate)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_estimates()  # Load estimates on initialization

    def load_estimates(self):
        """Load estimates from the database and display them in the table."""
        try:
            with Session(engine) as session:
                estimates = self.estimate_view.read_all(db_session=session)
                self.estimate_table.setRowCount(len(estimates))
                self.estimate_table.setColumnCount(6)
                self.estimate_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Estimate Date",
                        "Total Amount",
                        "Status",
                        "Description",
                        "Customer ID",
                        "Vehicle ID",
                    ]
                )

                for row, estimate in enumerate(estimates):
                    self.estimate_table.setItem(
                        row, 0, QTableWidgetItem(str(estimate.id))
                    )
                    self.estimate_table.setItem(
                        row, 1, QTableWidgetItem(str(estimate.estimate_date))
                    )
                    self.estimate_table.setItem(
                        row,
                        2,
                        QTableWidgetItem(str(estimate.total_estimate_amount)),
                    )
                    self.estimate_table.setItem(
                        row, 3, QTableWidgetItem(estimate.status)
                    )
                    self.estimate_table.setItem(
                        row, 4, QTableWidgetItem(estimate.description or "")
                    )
                    self.estimate_table.setItem(
                        row, 5, QTableWidgetItem(str(estimate.customer_id))
                    )
                    self.estimate_table.setItem(
                        row, 6, QTableWidgetItem(str(estimate.vehicle_id))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load estimates: {e!s}"
            )

    def add_estimate(self):
        """Add a new estimate to the database."""
        dialog = EstimateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    vehicle = session.exec(
                        select(Vehicle)
                        .where(Vehicle.id == UUID(data["vehicle_id"]))
                    ).first()
                    if not vehicle:
                        raise ValueError("Vehicle not found")

                    new_estimate = Estimate(
                        estimate_date=datetime.now(),
                        total_estimate_amount=data["total_amount"],
                        status=data["status"],
                        description=data["description"],
                        customer_id=vehicle.customer_id,
                        vehicle_id=vehicle.id,
                    )
                    self.estimate_view.create(
                        db_session=session, record=new_estimate
                    )
                    QMessageBox.information(
                        self, "Success", "Estimate added successfully!"
                    )
                    self.load_estimates()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add estimate: {e!s}"
                )

    def update_estimate(self):
        """Update an existing estimate."""
        selected_row = self.estimate_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select an estimate to update."
            )
            return

        item = self.estimate_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected estimate ID is invalid."
            )
            return
        estimate_id = item.text()

        dialog = EstimateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    vehicle = session.exec(
                        select(Vehicle)
                        .where(Vehicle.id == UUID(data["vehicle_id"]))
                    ).first()
                    if not vehicle:
                        raise ValueError("Vehicle not found")

                    estimate_obj = self.estimate_view.read_by_id(
                        db_session=session, record_id=UUID(estimate_id)
                    )
                    if estimate_obj:
                        estimate_obj.estimate_date = datetime.now()
                        estimate_obj.total_estimate_amount = data[
                            "total_amount"
                        ]
                        estimate_obj.status = data["status"]
                        estimate_obj.description = data["description"]
                        estimate_obj.customer_id = vehicle.customer_id
                        estimate_obj.vehicle_id = vehicle.id
                        self.estimate_view.update(
                            db_session=session,
                            record_id=UUID(estimate_id),
                            record=estimate_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Estimate updated successfully!"
                        )
                        self.load_estimates()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update estimate: {e!s}"
                )

    def delete_estimate(self):
        """Delete an estimate from the database."""
        try:
            selected_row = self.estimate_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an estimate to delete."
                )
                return

            item = self.estimate_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected estimate ID is invalid."
                )
                return
            estimate_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Estimate",
                "Are you sure you want to delete this estimate?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.estimate_view.delete(
                        db_session=session, record_id=UUID(estimate_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Estimate deleted successfully!"
                    )
                    self.load_estimates()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete estimate: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = EstimateGUI()
    window.show()
    app.exec()
