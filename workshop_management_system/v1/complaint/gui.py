"""Complaint GUI Module."""

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
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.complaint.model import Complaint
from workshop_management_system.v1.complaint.view import ComplaintView
from workshop_management_system.v1.customer.model import Customer


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

                self.addItem("Select a customer...")
                self.customer_ids.append(None)

                for customer in customers:
                    self.customer_ids.append(customer.id)
                    display_text = (
                        f"<b>{customer.name}</b> "
                        f"<font color='#666666'>{
                            customer.mobile_number
                        }</font>"
                    )
                    self.addItem(display_text)
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load customers: {e!s}"
            )

    def get_selected_customer_id(self) -> int | None:
        """Get the ID of the selected customer."""
        current_index = self.currentIndex()
        if current_index > 0 and current_index < len(self.customer_ids):
            return self.customer_ids[current_index]
        return None


class ComplaintGUI(QMainWindow):
    """Complaint GUI Class."""

    def __init__(self) -> None:
        """Initialize the Complaint GUI."""
        super().__init__()
        self.setWindowTitle("Complaint Management")
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
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)

        self.complaint_view = ComplaintView(model=Complaint)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Complaint Management")
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

        # Complaints table
        self.complaint_table = QTableWidget()
        self.complaint_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.complaint_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.complaint_table)
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
            ("Load Complaints", self.load_complaints),
            ("Add Complaint", self.add_complaint),
            ("Update Complaint", self.update_complaint),
            ("Delete Complaint", self.delete_complaint),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)
        self.load_complaints()

    def create_input_dialog(
        self, title: str, complaint: Complaint | None = None
    ) -> tuple[QDialog, dict]:
        """Create a dialog for complaint input."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        inputs = {}

        # Customer selection
        inputs["customer"] = CustomerComboBox(dialog)
        layout.addRow("Customer:", inputs["customer"])

        # Description
        inputs["description"] = QTextEdit(dialog)
        inputs["description"].setMaximumHeight(100)
        if complaint:
            inputs["description"].setText(complaint.description)
        layout.addRow("Description:", inputs["description"])

        # Priority
        inputs["priority"] = QComboBox(dialog)
        inputs["priority"].addItems(["Low", "Medium", "High"])
        if complaint:
            inputs["priority"].setCurrentText(complaint.priority)
        layout.addRow("Priority:", inputs["priority"])

        # Status
        inputs["status"] = QComboBox(dialog)
        inputs["status"].addItems(["New", "In Progress", "Resolved", "Closed"])
        if complaint:
            inputs["status"].setCurrentText(complaint.status)
        layout.addRow("Status:", inputs["status"])

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog, inputs

    def load_complaints(self) -> None:
        """Load complaints from database."""
        try:
            with Session(engine) as session:
                complaints = self.complaint_view.read_all(db_session=session)
                self.complaint_table.setRowCount(len(complaints))
                self.complaint_table.setColumnCount(5)
                self.complaint_table.setHorizontalHeaderLabels(
                    ["ID", "Customer", "Description", "Priority", "Status"]
                )

                for row, complaint in enumerate(complaints):
                    customer = session.get(Customer, complaint.customer_id)
                    self.complaint_table.setItem(
                        row, 0, QTableWidgetItem(str(complaint.id))
                    )
                    self.complaint_table.setItem(
                        row,
                        1,
                        QTableWidgetItem(customer.name if customer else ""),
                    )
                    self.complaint_table.setItem(
                        row, 2, QTableWidgetItem(complaint.description)
                    )
                    self.complaint_table.setItem(
                        row, 3, QTableWidgetItem(complaint.priority)
                    )
                    self.complaint_table.setItem(
                        row, 4, QTableWidgetItem(complaint.status)
                    )

                self.complaint_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load complaints: {e!s}"
            )

    def add_complaint(self) -> None:
        """Add a new complaint to the database."""
        try:
            dialog, inputs = self.create_input_dialog("Add Complaint")

            if dialog.exec() == QDialog.DialogCode.Accepted:
                customer_id = inputs["customer"].get_selected_customer_id()
                if not customer_id:
                    QMessageBox.critical(
                        self, "Error", "Please select a customer."
                    )
                    return

                with Session(engine) as session:
                    new_complaint = Complaint(
                        description=inputs["description"].toPlainText(),
                        priority=inputs["priority"].currentText(),
                        status=inputs["status"].currentText(),
                        customer_id=customer_id,
                    )
                    self.complaint_view.create(
                        db_session=session, record=new_complaint
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint added successfully!"
                    )
                    self.load_complaints()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add complaint: {e!s}"
            )

    def update_complaint(self) -> None:
        """Update an existing complaint."""
        try:
            selected_row = self.complaint_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a complaint to update."
                )
                return

            item = self.complaint_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected complaint ID is invalid."
                )
                return
            complaint_id = int(item.text())

            with Session(engine) as session:
                complaint_obj = self.complaint_view.read_by_id(
                    db_session=session, record_id=complaint_id
                )
                if not complaint_obj:
                    QMessageBox.warning(self, "Error", "Complaint not found.")
                    return

                dialog, inputs = self.create_input_dialog(
                    "Update Complaint", complaint_obj
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    customer_id = inputs["customer"].get_selected_customer_id()
                    if not customer_id:
                        QMessageBox.critical(
                            self, "Error", "Please select a customer."
                        )
                        return

                    complaint_obj.description = inputs[
                        "description"
                    ].toPlainText()
                    complaint_obj.priority = inputs["priority"].currentText()
                    complaint_obj.status = inputs["status"].currentText()
                    complaint_obj.customer_id = customer_id

                    self.complaint_view.update(
                        db_session=session,
                        record_id=complaint_id,
                        record=complaint_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint updated successfully!"
                    )
                    self.load_complaints()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update complaint: {e!s}"
            )

    def delete_complaint(self) -> None:
        """Delete a complaint from the database."""
        try:
            selected_row = self.complaint_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a complaint to delete."
                )
                return

            item = self.complaint_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected complaint ID is invalid."
                )
                return
            complaint_id = int(item.text())

            confirmation = QMessageBox.question(
                self,
                "Delete Complaint",
                "Are you sure you want to delete this complaint?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.complaint_view.delete(
                        db_session=session, record_id=complaint_id
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint deleted successfully!"
                    )
                    self.load_complaints()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete complaint: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = ComplaintGUI()
    window.show()
    app.exec()
