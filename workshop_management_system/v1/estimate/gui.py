"""Estimate GUI Module.

Description:
- This module provides the GUI for managing estimates.

"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
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
    QToolBar,
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

    def __init__(self, parent=None) -> None:
        """Initialize the Estimate Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Estimate Details")
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

        self.total_amount_input = QLineEdit(self)
        self.status_input = QLineEdit(self)
        self.description_input = QLineEdit(self)
        self.valid_until_input = QLineEdit(self)
        self.vehicle_id_input = QLineEdit(self)
        self.job_card_id_input = QLineEdit(self)
        self.customer_id_input = QLineEdit(self)

        self.form_layout.addRow(
            "Total Estimate Amount:", self.total_amount_input
        )
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow(
            "Description (optional):", self.description_input
        )
        self.form_layout.addRow(
            "Valid Until (YYYY-MM-DD):", self.valid_until_input
        )
        self.form_layout.addRow("Vehicle ID:", self.vehicle_id_input)
        self.form_layout.addRow(
            "Job Card ID (optional):", self.job_card_id_input
        )
        self.form_layout.addRow("Customer ID:", self.customer_id_input)

        self.buttons = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            ),
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
            "valid_until": self.valid_until_input.text(),
            "vehicle_id": self.vehicle_id_input.text(),
            "job_card_id": self.job_card_id_input.text(),
            "customer_id": self.customer_id_input.text(),
        }


class EstimateGUI(QWidget):
    """Estimate GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Estimate GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.setStyleSheet("""
            QWidget {
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
                min-width: 125px;
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

        self.estimate_view = EstimateView(model=Estimate)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Estimate Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        main_layout.addWidget(
            back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

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

        # Estimate table
        self.estimate_table = QTableWidget()
        self.estimate_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.estimate_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.estimate_table)
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
            ("Load Estimates", self.load_estimates),
            ("Add Estimate", self.add_estimate),
            ("Update Estimate", self.update_estimate),
            ("Delete Estimate", self.delete_estimate),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_estimates()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_estimates(self) -> None:
        """Load estimates from the database and display them in the table."""
        try:
            with Session(engine) as session:
                estimates = self.estimate_view.read_all(db_session=session)
                self.estimate_table.setRowCount(len(estimates))
                self.estimate_table.setColumnCount(9)
                self.estimate_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Estimate Date",
                        "Total Amount",
                        "Status",
                        "Description",
                        "Valid Until",
                        "Customer ID",
                        "Vehicle ID",
                        "Job Card ID",
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
                        row, 5, QTableWidgetItem(str(estimate.valid_until))
                    )
                    self.estimate_table.setItem(
                        row, 6, QTableWidgetItem(str(estimate.customer_id))
                    )
                    self.estimate_table.setItem(
                        row, 7, QTableWidgetItem(str(estimate.vehicle_id))
                    )
                    self.estimate_table.setItem(
                        row,
                        8,
                        QTableWidgetItem(
                            str(estimate.job_card_id)
                            if estimate.job_card_id
                            else ""
                        ),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load estimates: {e!s}"
            )

    def add_estimate(self) -> None:
        """Add a new estimate to the database."""
        dialog = EstimateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    vehicle = session.exec(
                        select(Vehicle).where(
                            Vehicle.id == int(data["vehicle_id"])
                        )
                    ).first()
                    if not vehicle:
                        raise ValueError("Vehicle not found")

                    new_estimate = Estimate(
                        estimate_date=datetime.now(),
                        total_estimate_amount=data["total_amount"],
                        status=data["status"],
                        description=data["description"],
                        valid_until=datetime.strptime(
                            data["valid_until"], "%Y-%m-%d"
                        ),
                        customer_id=vehicle.customer_id,
                        vehicle_id=vehicle.id,
                        job_card_id=int(data["job_card_id"])
                        if data["job_card_id"]
                        else None,
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

    def update_estimate(self) -> None:
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
                        select(Vehicle).where(
                            Vehicle.id == int(data["vehicle_id"])
                        )
                    ).first()
                    if not vehicle:
                        raise ValueError("Vehicle not found")

                    estimate_obj = self.estimate_view.read_by_id(
                        db_session=session, record_id=int(estimate_id)
                    )
                    if estimate_obj:
                        estimate_obj.estimate_date = datetime.now()
                        estimate_obj.total_estimate_amount = data[
                            "total_amount"
                        ]
                        estimate_obj.status = data["status"]
                        estimate_obj.description = data["description"]
                        estimate_obj.valid_until = datetime.strptime(
                            data["valid_until"], "%Y-%m-%d"
                        )
                        estimate_obj.customer_id = vehicle.customer_id
                        estimate_obj.vehicle_id = vehicle.id
                        estimate_obj.job_card_id = (
                            int(data["job_card_id"])
                            if data["job_card_id"]
                            else None
                        )
                        self.estimate_view.update(
                            db_session=session,
                            record_id=int(estimate_id),
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

    def delete_estimate(self) -> None:
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
                        db_session=session, record_id=int(estimate_id)
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
