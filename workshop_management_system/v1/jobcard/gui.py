"""JobCard GUI Module.

Description:
- This module provides the GUI for managing job cards.

"""

from datetime import datetime

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
    QHeaderView,
    QLabel,
    QLineEdit,
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
from workshop_management_system.v1.vehicle.model import Vehicle


class JobCardDialog(QDialog):
    """Dialog for adding/updating a job card."""

    def __init__(self, parent=None) -> None:
        """Initialize the JobCard Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Job Card Details")
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

        self.vehicle_id_input = QComboBox(self)
        self.load_vehicles()
        self.service_date_input = QLineEdit(self)
        self.service_date_input.setText(
            datetime.now().strftime("%Y-%m-%d")
        )  # Auto-fill current date
        self.status_input = QLineEdit(self)
        self.total_amount_input = QLineEdit(self)
        self.description_input = QLineEdit(self)

        self.form_layout.addRow("Vehicle ID:", self.vehicle_id_input)
        self.form_layout.addRow(
            "Service Date (YYYY-MM-DD):", self.service_date_input
        )
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow("Total Amount:", self.total_amount_input)
        self.form_layout.addRow("Description:", self.description_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def load_vehicles(self):
        """Load vehicles from the database and populate the dropdown."""
        try:
            with Session(engine) as session:
                vehicles = session.query(Vehicle).all()
                for vehicle in vehicles:
                    self.vehicle_id_input.addItem(
                        f"{vehicle.id} - {vehicle.vehicle_number}", vehicle.id
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def get_data(self):
        """Get the data from the dialog."""
        return {
            "vehicle_id": self.vehicle_id_input.currentData(),
            "service_date": self.service_date_input.text(),
            "status": self.status_input.text(),
            "total_amount": float(self.total_amount_input.text()),
            "description": self.description_input.text(),
        }


# ... (previous code remains the same)


class JobCardGUI(QWidget):
    """JobCard GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the JobCard GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #87CEEB;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                min-width: 125px;
                margin: 0px;
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid black;  /* Add border to the table */
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #87CEEB;
                color: white;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: none;
            }
            QLabel {
                color: black;
            }
        """)

        self.jobcard_view = JobCardView(model=JobCard)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Job Card Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search job cards...")
        self.search_input.textChanged.connect(self.search_jobcards)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Vehicle ID", "Service Date", "Status", "Description"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_jobcards)

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_criteria)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        main_layout.addWidget(
            back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Table Frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.NoFrame)
        table_layout = QVBoxLayout(table_frame)

        # JobCard table
        self.jobcard_table = QTableWidget()
        self.jobcard_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.jobcard_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.jobcard_table.setAlternatingRowColors(True)
        self.jobcard_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid black;  /* Add border to the table */
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: 87CEEB;
                color: white;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: none;
            }
        """)
        self.jobcard_table.verticalHeader().setVisible(False)
        self.jobcard_table.horizontalHeader().setVisible(False)
        self.jobcard_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.jobcard_table.horizontalHeader().setStretchLastSection(True)
        self.jobcard_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_layout.addWidget(self.jobcard_table)
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
            ("Load Job Cards", self.load_jobcards),
            ("Add Job Card", self.add_jobcard),
            ("Update Job Card", self.update_jobcard),
            ("Delete Job Card", self.delete_jobcard),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_jobcards()

    # ... (rest of the code remains the same)

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_jobcards(self) -> None:
        """Load job cards from the database and display them in the table."""
        try:
            with Session(engine) as session:
                jobcards = self.jobcard_view.read_all(db_session=session)
                self.jobcard_table.setRowCount(len(jobcards) + 1)
                self.jobcard_table.setColumnCount(6)
                self.jobcard_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Vehicle ID",
                        "Service Date",
                        "Status",
                        "Total Amount",
                        "Description",
                    ]
                )

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Vehicle ID",
                    "Service Date",
                    "Status",
                    "Total Amount",
                    "Description",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.jobcard_table.setItem(0, col, item)

                # Set the height of the first row
                self.jobcard_table.setRowHeight(0, 40)

                for row, jobcard in enumerate(jobcards, start=1):
                    self.jobcard_table.setItem(
                        row, 0, QTableWidgetItem(str(jobcard.id))
                    )
                    self.jobcard_table.setItem(
                        row, 1, QTableWidgetItem(str(jobcard.vehicle_id))
                    )
                    self.jobcard_table.setItem(
                        row, 2, QTableWidgetItem(str(jobcard.service_date))
                    )
                    self.jobcard_table.setItem(
                        row, 3, QTableWidgetItem(jobcard.status)
                    )
                    self.jobcard_table.setItem(
                        row, 4, QTableWidgetItem(str(jobcard.total_amount))
                    )
                    self.jobcard_table.setItem(
                        row, 5, QTableWidgetItem(jobcard.description)
                    )

                # Adjust column widths
                self.jobcard_table.resizeColumnsToContents()
                self.jobcard_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.jobcard_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load job cards: {e!s}"
            )

    def add_jobcard(self) -> None:
        """Add a new job card to the database."""
        dialog = JobCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    new_jobcard = JobCard(
                        vehicle_id=data["vehicle_id"],
                        service_date=datetime.strptime(
                            data["service_date"], "%Y-%m-%d"
                        ),
                        status=data["status"],
                        total_amount=data["total_amount"],
                        description=data["description"],
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

    def update_jobcard(self) -> None:
        """Update an existing job card."""
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
        jobcard_id = item.text()

        dialog = JobCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    jobcard_obj = self.jobcard_view.read_by_id(
                        db_session=session, record_id=int(jobcard_id)
                    )
                    if jobcard_obj:
                        jobcard_obj.vehicle_id = data["vehicle_id"]
                        jobcard_obj.service_date = datetime.strptime(
                            data["service_date"], "%Y-%m-%d"
                        )
                        jobcard_obj.status = data["status"]
                        jobcard_obj.total_amount = data["total_amount"]
                        jobcard_obj.description = data["description"]
                        self.jobcard_view.update(
                            db_session=session,
                            record_id=int(jobcard_id),
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

    def delete_jobcard(self) -> None:
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
            jobcard_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Job Card",
                "Are you sure you want to delete this job card?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.jobcard_view.delete(
                        db_session=session, record_id=int(jobcard_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Job card deleted successfully!"
                    )
                    self.load_jobcards()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete job card: {e!s}"
            )

    def search_jobcards(self) -> None:
        """Filter job cards based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.jobcard_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "vehicle id":
                    cell_text = self.jobcard_table.item(row, 1)
                elif criteria == "service date":
                    cell_text = self.jobcard_table.item(row, 2)
                elif criteria == "status":
                    cell_text = self.jobcard_table.item(row, 3)
                elif criteria == "description":
                    cell_text = self.jobcard_table.item(row, 5)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.jobcard_table.setRowHidden(row, not show_row)


if __name__ == "__main__":
    app = QApplication([])
    window = JobCardGUI()
    window.show()
    app.exec()
