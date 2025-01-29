"""JobCard GUI Module.

Description:
- This module provides the GUI for managing job cards.

"""

from datetime import datetime

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
from workshop_management_system.v1.jobcard.model import JobCard
from workshop_management_system.v1.jobcard.view import JobCardView


class JobCardGUI(QMainWindow):
    """JobCard GUI Class.

    Description:
    - This class provides the GUI for managing job cards.

    """

    def __init__(self):
        """Initialize the JobCard GUI."""
        super().__init__()
        self.setWindowTitle("Job Card Management")
        self.setGeometry(100, 100, 800, 600)

        self.jobcard_view = JobCardView(
            model=JobCard
        )  # Initialize JobCardView for CRUD operations

        self.main_layout = QVBoxLayout()

        # JobCard table
        self.jobcard_table = QTableWidget()
        self.jobcard_table.setSelectionBehavior(
            self.jobcard_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.jobcard_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Job Cards")
        self.load_button.clicked.connect(self.load_jobcards)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Job Card")
        self.add_button.clicked.connect(self.add_jobcard)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Job Card")
        self.update_button.clicked.connect(self.update_jobcard)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Job Card")
        self.delete_button.clicked.connect(self.delete_jobcard)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_jobcards()  # Load job cards on initialization

    def load_jobcards(self):
        """Load job cards from the database and display them in the table."""
        try:
            with Session(engine) as session:
                jobcards = self.jobcard_view.read_all(db_session=session)
                self.jobcard_table.setRowCount(len(jobcards))
                self.jobcard_table.setColumnCount(7)
                self.jobcard_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Customer ID",
                        "Vehicle ID",
                        "Service Date",
                        "Status",
                        "Total Amount",
                        "Supervisor ID",
                        "Mechanic ID",
                    ]
                )

                for row, jobcard in enumerate(jobcards):
                    self.jobcard_table.setItem(
                        row, 0, QTableWidgetItem(str(jobcard.id))
                    )
                    self.jobcard_table.setItem(
                        row, 1, QTableWidgetItem(str(jobcard.customer_id))
                    )
                    self.jobcard_table.setItem(
                        row, 2, QTableWidgetItem(str(jobcard.vehicle_id))
                    )
                    self.jobcard_table.setItem(
                        row, 3, QTableWidgetItem(str(jobcard.service_date))
                    )
                    self.jobcard_table.setItem(
                        row, 4, QTableWidgetItem(jobcard.status)
                    )
                    self.jobcard_table.setItem(
                        row, 5, QTableWidgetItem(str(jobcard.total_amount))
                    )
                    self.jobcard_table.setItem(
                        row, 6, QTableWidgetItem(str(jobcard.supervisor_id))
                    )
                    self.jobcard_table.setItem(
                        row, 7, QTableWidgetItem(str(jobcard.mechanic_id))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load job cards: {e!s}"
            )

    def add_jobcard(self):
        """Add a new job card to the database."""
        try:
            # Get job card details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Add Job Card", "Enter Customer ID:"
            )
            if not ok:
                return

            vehicle_id, ok = QInputDialog.getInt(
                self, "Add Job Card", "Enter Vehicle ID:"
            )
            if not ok:
                return

            service_date, ok = QInputDialog.getText(
                self, "Add Job Card", "Enter Service Date (YYYY-MM-DD):"
            )
            if not ok or not service_date:
                return

            status, ok = QInputDialog.getText(
                self, "Add Job Card", "Enter Status:"
            )
            if not ok or not status:
                return

            total_amount, ok = QInputDialog.getDouble(
                self, "Add Job Card", "Enter Total Amount:"
            )
            if not ok:
                return

            supervisor_id, ok = QInputDialog.getInt(
                self, "Add Job Card", "Enter Supervisor ID:"
            )
            if not ok:
                return

            mechanic_id, ok = QInputDialog.getInt(
                self, "Add Job Card", "Enter Mechanic ID:"
            )
            if not ok:
                return

            with Session(engine) as session:
                new_jobcard = JobCard(
                    # id will be auto-generated by the database
                    customer_id=customer_id,
                    service_date=datetime.strptime(service_date, "%Y-%m-%d"),
                    vehicle_id=vehicle_id,
                    status=status,
                    total_amount=total_amount,
                    supervisor_id=supervisor_id,
                    mechanic_id=mechanic_id,
                )
                self.jobcard_view.create(
                    db_session=session, record=new_jobcard
                )
                QMessageBox.information(
                    self, "Success", "Job card added successfully!"
                )
                self.load_jobcards()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add job card: {e!s}"
            )

    def update_jobcard(self):
        """Update an existing job card."""
        try:
            selected_row = self.jobcard_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a job card to update."
                )
                return

            item = self.jobcard_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected job card ID is invalid."
                )
                return
            jobcard_id = int(item.text())

            # Get updated details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Update Job Card", "Enter New Customer ID:"
            )
            if not ok:
                return

            vehicle_id, ok = QInputDialog.getInt(
                self, "Update Job Card", "Enter New Vehicle ID:"
            )
            if not ok:
                return

            service_date, ok = QInputDialog.getText(
                self, "Update Job Card", "Enter New Service Date (YYYY-MM-DD):"
            )
            if not ok or not service_date:
                return

            status, ok = QInputDialog.getText(
                self, "Update Job Card", "Enter New Status:"
            )
            if not ok or not status:
                return

            total_amount, ok = QInputDialog.getDouble(
                self, "Update Job Card", "Enter New Total Amount:"
            )
            if not ok:
                return

            supervisor_id, ok = QInputDialog.getInt(
                self, "Update Job Card", "Enter New Supervisor ID:"
            )
            if not ok:
                return

            mechanic_id, ok = QInputDialog.getInt(
                self, "Update Job Card", "Enter New Mechanic ID:"
            )
            if not ok:
                return

            with Session(engine) as session:
                jobcard_obj = self.jobcard_view.read_by_id(
                    db_session=session, record_id=jobcard_id
                )
                if jobcard_obj:
                    jobcard_obj.customer_id = customer_id
                    jobcard_obj.vehicle_id = vehicle_id
                    jobcard_obj.service_date = datetime.strptime(
                        service_date, "%Y-%m-%d"
                    )
                    jobcard_obj.status = status
                    jobcard_obj.total_amount = total_amount
                    jobcard_obj.supervisor_id = supervisor_id
                    jobcard_obj.mechanic_id = mechanic_id
                    self.jobcard_view.update(
                        db_session=session,
                        record_id=jobcard_id,
                        record=jobcard_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Job card updated successfully!"
                    )
                    self.load_jobcards()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update job card: {e!s}"
            )

    def delete_jobcard(self):
        """Delete a job card from the database."""
        try:
            selected_row = self.jobcard_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a job card to delete."
                )
                return

            item = self.jobcard_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected job card ID is invalid."
                )
                return
            jobcard_id = int(item.text())

            confirmation = QMessageBox.question(
                self,
                "Delete Job Card",
                "Are you sure you want to delete this job card?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.jobcard_view.delete(
                        db_session=session, record_id=jobcard_id
                    )
                    QMessageBox.information(
                        self, "Success", "Job card deleted successfully!"
                    )
                    self.load_jobcards()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete job card: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = JobCardGUI()
    window.show()
    app.exec()
