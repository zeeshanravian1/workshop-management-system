"""Vehicle GUI Module."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
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


class CustomerComboBox(QComboBox):
    """Custom ComboBox for customer selection."""

    def __init__(self, parent=None) -> None:
        """Initialize CustomerComboBox."""
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                border: 2px solid #4CAF50;
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
                margin-top: -5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
        """)
        self.customer_ids = []
        self.load_customers()

    def load_customers(self) -> None:
        """Load customers into combo box."""
        try:
            with Session(engine) as session:
                customers = session.exec(select(Customer)).all()
                self.clear()
                self.customer_ids.clear()
                # Add a default placeholder item
                self.addItem("Select a customer...")
                self.customer_ids.append(None)
                for customer in customers:
                    self.customer_ids.append(customer.id)
                    display_text = (
                        f"<span style='font-weight:bold;'>"
                        f"{customer.name}</span> "
                        f"<span style='color:#666666;'>"
                        f"({customer.mobile_number})</span>"
                    )
                    self.addItem(display_text)
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load customers: {e!s}"
            )

    def get_selected_customer_id(self) -> int | None:
        """Get the ID of the selected customer."""
        current_index = self.currentIndex()
        if current_index >= 0 and current_index < len(self.customer_ids):
            return self.customer_ids[current_index]
        return None

    def set_customer_by_id(self, customer_id: int) -> None:
        """Set the current selection by customer ID."""
        try:
            index = self.customer_ids.index(customer_id)
            self.setCurrentIndex(index)
        except ValueError:
            self.setCurrentIndex(-1)


class VehicleGUI(QMainWindow):
    """Vehicle GUI Class."""

    def __init__(self) -> None:
        """Initialize the Vehicle GUI."""
        super().__init__()
        self.setWindowTitle("Vehicle Management")
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
            }
            QLabel {
                color: #333;
            }
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)

        self.vehicle_view = VehicleView(model=Vehicle)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Vehicle Management")
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

        # Vehicle table
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.vehicle_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.vehicle_table)
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
            ("Load Vehicles", self.load_vehicles),
            ("Add Vehicle", self.add_vehicle),
            ("Update Vehicle", self.update_vehicle),
            ("Delete Vehicle", self.delete_vehicle),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_vehicles()

    def load_vehicles(self) -> None:
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
                        row,
                        6,
                        QTableWidgetItem(customer.name if customer else ""),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def create_input_dialog(
        self, title: str, vehicle: Vehicle | None = None
    ) -> tuple[QDialog, dict]:
        """Create a dialog for vehicle input."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)  # Set minimum width for better visibility
        dialog.setStyleSheet("""
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
        layout = QFormLayout(dialog)

        # Create input fields
        inputs = {}
        fields = [
            ("make", "Make", QLineEdit),
            ("model", "Model", QLineEdit),
            ("year", "Year", QLineEdit),
            ("chassis_number", "Chassis Number", QLineEdit),
            ("engine_number", "Engine Number", QLineEdit),
            ("customer", "Customer", CustomerComboBox),
        ]

        for field_name, label, widget_class in fields:
            input_field = widget_class(dialog)
            if vehicle and field_name != "customer":
                input_field.setText(str(getattr(vehicle, field_name)))
            inputs[field_name] = input_field
            layout.addRow(f"{label}:", input_field)

        # Set customer if updating
        if vehicle:
            inputs["customer"].set_customer_by_id(vehicle.customer_id)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog, inputs

    def add_vehicle(self) -> None:
        """Add a new vehicle to the database."""
        try:
            dialog, inputs = self.create_input_dialog("Add Vehicle")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                customer_id = inputs["customer"].get_selected_customer_id()
                if not customer_id:
                    QMessageBox.critical(
                        self, "Error", "Please select a customer."
                    )
                    return

                with Session(engine) as session:
                    new_vehicle = Vehicle(
                        make=inputs["make"].text(),
                        model=inputs["model"].text(),
                        year=int(inputs["year"].text()),
                        chassis_number=inputs["chassis_number"].text(),
                        engine_number=inputs["engine_number"].text(),
                        customer_id=customer_id,
                    )
                    self.vehicle_view.create(
                        db_session=session, 
                        record=new_vehicle
                    )
                    QMessageBox.information(
                        self, "Success", "Vehicle added successfully!"
                    )
                    self.load_vehicles()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add vehicle: {e!s}"
            )

    def update_vehicle(self) -> None:
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
            vehicle_id = int(item.text())

            with Session(engine) as session:
                vehicle_obj = self.vehicle_view.read_by_id(
                    db_session=session, record_id=vehicle_id
                )
                if not vehicle_obj:
                    QMessageBox.warning(self, "Error", "Vehicle not found.")
                    return

                dialog, inputs = self.create_input_dialog(
                    "Update Vehicle", vehicle_obj
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    customer_id = inputs["customer"].get_selected_customer_id()
                    if not customer_id:
                        QMessageBox.critical(
                            self, "Error", "Please select a customer."
                        )
                        return

                    vehicle_obj.make = inputs["make"].text()
                    vehicle_obj.model = inputs["model"].text()
                    vehicle_obj.year = int(inputs["year"].text())
                    vehicle_obj.chassis_number = inputs["chassis_number"].text()
                    vehicle_obj.engine_number = inputs["engine_number"].text()
                    vehicle_obj.customer_id = customer_id

                    self.vehicle_view.update(
                        db_session=session,
                        record_id=vehicle_id,
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

    def delete_vehicle(self) -> None:
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
