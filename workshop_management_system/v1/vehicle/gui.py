"""Vehicle GUI Module.

Description:
- This module provides the GUI for managing vehicles.

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
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView


class VehicleGUI(QMainWindow):
    """Vehicle GUI Class.

    Description:
    - This class provides the GUI for managing vehicles.

    """

    def __init__(self) -> None:
        """Initialize the Vehicle GUI."""
        super().__init__()
        self.setWindowTitle("Vehicle Management")
        self.setGeometry(100, 100, 800, 600)

        self.vehicle_view = VehicleView(
            model=Vehicle
        )  # Initialize VehicleView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Vehicle table
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setSelectionBehavior(
            self.vehicle_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.vehicle_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Vehicles")
        self.load_button.clicked.connect(self.load_vehicles)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Vehicle")
        self.add_button.clicked.connect(self.add_vehicle)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Vehicle")
        self.update_button.clicked.connect(self.update_vehicle)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Vehicle")
        self.delete_button.clicked.connect(self.delete_vehicle)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_vehicles()  # Load vehicles on initialization

    def load_vehicles(self):
        """Load vehicles from the database and display them in the table."""
        try:
            with Session(engine) as session:
                vehicles = self.vehicle_view.read_all(db_session=session)
                self.vehicle_table.setRowCount(len(vehicles))
                self.vehicle_table.setColumnCount(7)
                self.vehicle_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Make",
                        "Model",
                        "Year",
                        "Chassis Number",
                        "Engine Number",
                        "Customer Name",
                    ]
                )

                for row, vehicle in enumerate(vehicles):
                    customer = session.exec(
                        select(Customer).where(
                            Customer.id == vehicle.customer_id
                        )
                    ).first()
                    self.vehicle_table.setItem(
                        row, 0, QTableWidgetItem(str(vehicle.id))
                    )
                    self.vehicle_table.setItem(
                        row, 1, QTableWidgetItem(vehicle.make)
                    )
                    self.vehicle_table.setItem(
                        row, 2, QTableWidgetItem(vehicle.model)
                    )
                    self.vehicle_table.setItem(
                        row, 3, QTableWidgetItem(str(vehicle.year))
                    )
                    self.vehicle_table.setItem(
                        row, 4, QTableWidgetItem(vehicle.chassis_number)
                    )
                    self.vehicle_table.setItem(
                        row, 5, QTableWidgetItem(vehicle.engine_number)
                    )
                    self.vehicle_table.setItem(
                        row, 6, QTableWidgetItem(
                            customer.name if customer else ""
                        )
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def add_vehicle(self):
        """Add a new vehicle to the database."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Vehicle")
            layout = QFormLayout(dialog)

            make_input = QLineEdit(dialog)
            model_input = QLineEdit(dialog)
            year_input = QLineEdit(dialog)
            chassis_number_input = QLineEdit(dialog)
            engine_number_input = QLineEdit(dialog)
            customer_name_input = QLineEdit(dialog)

            layout.addRow("Make:", make_input)
            layout.addRow("Model:", model_input)
            layout.addRow("Year:", year_input)
            layout.addRow("Chassis Number:", chassis_number_input)
            layout.addRow("Engine Number:", engine_number_input)
            layout.addRow("Customer Name:", customer_name_input)

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel,
                dialog
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                make = make_input.text()
                model = model_input.text()
                year = int(year_input.text())
                chassis_number = chassis_number_input.text()
                engine_number = engine_number_input.text()
                customer_name = customer_name_input.text()

                with Session(engine) as session:
                    customer = session.exec(
                        select(Customer).where(
                            Customer.name == customer_name
                        )
                    ).first()
                    if not customer:
                        QMessageBox.critical(
                            self, "Error", "Customer not found."
                        )
                        return

                    new_vehicle = Vehicle(
                        make=make,
                        model=model,
                        year=year,
                        chassis_number=chassis_number,
                        engine_number=engine_number,
                        customer_id=customer.id,
                    )
                    self.vehicle_view.create(
                        db_session=session, record=new_vehicle
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle added successfully!"
                    )
                    self.load_vehicles()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add vehicle: {e!s}"
            )

    def update_vehicle(self):
        """Update an existing vehicle."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a vehicle to update."
                )
                return

            item = self.vehicle_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected vehicle ID is invalid."
                )
                return
            vehicle_id = item.text()

            dialog = QDialog(self)
            dialog.setWindowTitle("Update Vehicle")
            layout = QFormLayout(dialog)

            make_input = QLineEdit(dialog)
            model_input = QLineEdit(dialog)
            year_input = QLineEdit(dialog)
            chassis_number_input = QLineEdit(dialog)
            engine_number_input = QLineEdit(dialog)
            customer_name_input = QLineEdit(dialog)

            layout.addRow("Make:", make_input)
            layout.addRow("Model:", model_input)
            layout.addRow("Year:", year_input)
            layout.addRow("Chassis Number:", chassis_number_input)
            layout.addRow("Engine Number:", engine_number_input)
            layout.addRow("Customer Name:", customer_name_input)

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel,
                dialog
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                make = make_input.text()
                model = model_input.text()
                year = int(year_input.text())
                chassis_number = chassis_number_input.text()
                engine_number = engine_number_input.text()
                customer_name = customer_name_input.text()

                with Session(engine) as session:
                    vehicle_obj = self.vehicle_view.read_by_id(
                        db_session=session, record_id=int(vehicle_id)
                    )
                    if vehicle_obj:
                        customer = session.exec(
                            select(Customer).where(
                                Customer.name == customer_name
                            )
                        ).first()
                        if not customer:
                            QMessageBox.critical(
                                self, "Error", "Customer not found."
                            )
                            return

                        vehicle_obj.make = make
                        vehicle_obj.model = model
                        vehicle_obj.year = year
                        vehicle_obj.chassis_number = chassis_number
                        vehicle_obj.engine_number = engine_number
                        vehicle_obj.customer_id = customer.id
                        self.vehicle_view.update(
                            db_session=session,
                            record_id=int(vehicle_id),
                            record=vehicle_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Vehicle updated successfully!"
                        )
                        self.load_vehicles()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update vehicle: {e!s}"
            )

    def delete_vehicle(self):
        """Delete a vehicle from the database."""
        try:
            selected_row = self.vehicle_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a vehicle to delete."
                )
                return

            item = self.vehicle_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected vehicle ID is invalid."
                )
                return
            vehicle_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Vehicle",
                "Are you sure you want to delete this vehicle?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.vehicle_view.delete(
                        db_session=session, record_id=int(vehicle_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle deleted successfully!"
                    )
                    self.load_vehicles()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete vehicle: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = VehicleGUI()
    window.show()
    app.exec()
