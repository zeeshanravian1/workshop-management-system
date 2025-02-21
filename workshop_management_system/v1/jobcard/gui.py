import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
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
from workshop_management_system.v1.jobcard.model import JobCard
from workshop_management_system.v1.jobcard.view import JobCardView


# Embedded dialog for adding a job card.
class JobCardDialog(QDialog):
    """Dialog to add a new job card."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add New Job Card")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        # Status field using dropdown
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItem("Open")
        self.status_dropdown.addItem("Closed")
        self.service_date_input = QLineEdit()  # Format e.g., "YYYY-MM-DD"
        self.vehicle_id_input = QLineEdit()
        self.description_input = QLineEdit()
        layout.addRow("Status:", self.status_dropdown)
        layout.addRow("Service Date:", self.service_date_input)
        layout.addRow("Vehicle ID:", self.vehicle_id_input)
        layout.addRow("Description:", self.description_input)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """Return entered job card data."""
        return {
            "status": self.status_dropdown.currentText(),
            "service_date": self.service_date_input.text().strip(),
            "vehicle_id": int(self.vehicle_id_input.text().strip() or 0),
            "description": self.description_input.text().strip(),
        }


# Embedded dialog for updating a job card.
class JobCardUpdateDialog(QDialog):
    """Dialog to update an existing job card."""

    def __init__(self, initial_data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Update Job Card")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItem("Open")
        self.status_dropdown.addItem("Closed")
        # Set initial status
        status = initial_data.get("Status", "Open")
        index = self.status_dropdown.findText(status)
        if index != -1:
            self.status_dropdown.setCurrentIndex(index)
        self.service_date_input = QLineEdit(
            initial_data.get("Service Date", "")
        )
        self.vehicle_id_input = QLineEdit(
            str(initial_data.get("Vehicle ID", ""))
        )
        self.description_input = QLineEdit(initial_data.get("Description", ""))
        layout.addRow("Status:", self.status_dropdown)
        layout.addRow("Service Date:", self.service_date_input)
        layout.addRow("Vehicle ID:", self.vehicle_id_input)
        layout.addRow("Description:", self.description_input)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """Return updated job card data."""
        return {
            "status": self.status_dropdown.currentText(),
            "service_date": self.service_date_input.text().strip(),
            "vehicle_id": int(self.vehicle_id_input.text().strip() or 0),
            "description": self.description_input.text().strip(),
        }


class JobCardGUI(BaseGUI):
    """JobCard GUI Class."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # Insert header label with designated object name
        header = QLabel(
            "JobCard Management", alignment=Qt.AlignmentFlag.AlignCenter
        )
        header.setObjectName("headerLabel")
        self.layout().insertWidget(0, header)
        self.jobcard_view = JobCardView(JobCard)
        self.all_items = self.load_jobcards()
        self.filtered_items = self.all_items.copy()
        self.load_items()

    def get_search_criteria(self) -> list[str]:
        return ["ID", "Status", "Service Date", "Vehicle ID"]

    def load_jobcards(self) -> list[dict]:
        # Placeholder job card data based on jobcard/model.py fields
        return [
            {
                "ID": 1,
                "Status": "Open",
                "Service Date": "2023-10-01",
                "Vehicle ID": 101,
                "Description": "Oil change",
            },
            {
                "ID": 2,
                "Status": "Closed",
                "Service Date": "2023-09-15",
                "Vehicle ID": 102,
                "Description": "Brake replacement",
            },
        ]

    def load_items(self) -> None:
        self.customer_table.setRowCount(
            len(self.filtered_items) + 1
        )  # +1 for header
        self.customer_table.setColumnCount(5)
        headers = ["ID", "Status", "Service Date", "Vehicle ID", "Description"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)
        for row, data in enumerate(self.filtered_items, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(data["ID"]))
            )
            self.customer_table.setItem(
                row, 1, QTableWidgetItem(data["Status"])
            )
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(data["Service Date"])
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(str(data["Vehicle ID"]))
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(data["Description"])
            )

    def add_jobcard(self) -> None:
        """Open dialog to add a new job card."""
        dialog = JobCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            # Normally, create a JobCard record in the DB.
            QMessageBox.information(
                self,
                "JobCard Data",
                f"Status: {data['status']}\nService Date: {data['service_date']}\n"
                f"Vehicle ID: {data['vehicle_id']}\nDescription: {data['description']}",
            )

    def update_jobcard(self) -> None:
        """Open dialog to update the selected job card."""
        selected_row = self.customer_table.currentRow()
        if selected_row < 1:
            QMessageBox.warning(
                self, "Update", "Please select a job card to update."
            )
            return
        current_data = {
            "Status": self.customer_table.item(selected_row, 1).text(),
            "Service Date": self.customer_table.item(selected_row, 2).text(),
            "Vehicle ID": int(
                self.customer_table.item(selected_row, 3).text()
            ),
            "Description": self.customer_table.item(selected_row, 4).text(),
        }
        dialog = JobCardUpdateDialog(initial_data=current_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            # Normally, update the JobCard record in the DB.
            QMessageBox.information(
                self,
                "Updated JobCard Data",
                f"Status: {updated_data['status']}\nService Date: {updated_data['service_date']}\n"
                f"Vehicle ID: {updated_data['vehicle_id']}\nDescription: {updated_data['description']}",
            )

    def delete_jobcard(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Delete", "Delete job card functionality"
            )

    def show_context_menu(self, position) -> None:
        row = self.customer_table.rowAt(position.y())
        if row >= 0:
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            self.apply_styles(context_menu)
            update_action = context_menu.addAction("✏️  Update")
            update_action.setStatusTip("Update selected job card")
            context_menu.addSeparator()
            delete_action = context_menu.addAction("🗑️  Delete")
            delete_action.setStatusTip("Delete selected job card")
            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_jobcard()
            elif action == delete_action:
                self.delete_jobcard()

    def add(self) -> None:
        """Override base add method to open the add job card dialog."""
        self.add_jobcard()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    jobcard_gui = JobCardGUI(main_window)
    main_window.setCentralWidget(jobcard_gui)
    main_window.setWindowTitle("JobCard Management System")
    main_window.resize(800, 600)
    jobcard_gui.apply_styles(main_window)
    jobcard_gui.apply_styles()
    main_window.show()
    sys.exit(app.exec())
