import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from workshop_management_system.v1.base.gui import BaseGUI
from workshop_management_system.v1.jobcard.model import JobCard
from workshop_management_system.v1.jobcard.view import JobCardView


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
        QMessageBox.information(self, "Add", "Add job card functionality")

    def update_jobcard(self) -> None:
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Update", "Update job card functionality"
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
