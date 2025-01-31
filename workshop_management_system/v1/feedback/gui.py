"""Feedback GUI Module.

Description:
- This module provides the GUI for managing feedback.

"""

from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
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
from workshop_management_system.v1.employee.model import Employee
from workshop_management_system.v1.feedback.model import FeedBack
from workshop_management_system.v1.feedback.view import FeedBackView


class FeedbackDialog(QDialog):
    """Dialog for adding/updating feedback."""

    def __init__(self, parent=None) -> None:
        """Initialize the Feedback Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Feedback Details")
        self.form_layout = QFormLayout(self)

        self.description_input = QLineEdit(self)
        self.status_input = QLineEdit(self)
        self.customer_name_input = QLineEdit(self)
        self.employee_name_input = QLineEdit(self)

        self.form_layout.addRow("Description:", self.description_input)
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow("Customer Name:", self.customer_name_input)
        self.form_layout.addRow("Employee Name:", self.employee_name_input)

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
            "description": self.description_input.text(),
            "status": self.status_input.text(),
            "customer_name": self.customer_name_input.text(),
            "employee_name": self.employee_name_input.text(),
        }


class FeedBackGUI(QMainWindow):
    """Feedback GUI Class.

    Description:
    - This class provides the GUI for managing feedback.

    """

    def __init__(self):
        """Initialize the Feedback GUI."""
        super().__init__()
        self.setWindowTitle("Feedback Management")
        self.setGeometry(100, 100, 800, 600)

        self.feedback_view = FeedBackView(
            model=FeedBack
        )  # Initialize FeedBackView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Feedback table
        self.feedback_table = QTableWidget()
        self.feedback_table.setSelectionBehavior(
            self.feedback_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.feedback_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Feedback")
        self.load_button.clicked.connect(self.load_feedback)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Feedback")
        self.add_button.clicked.connect(self.add_feedback)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Feedback")
        self.update_button.clicked.connect(self.update_feedback)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Feedback")
        self.delete_button.clicked.connect(self.delete_feedback)
        button_layout.addWidget(self.delete_button)

        self.download_pdf_button = QPushButton("Download Feedback as PDF")
        self.download_pdf_button.clicked.connect(self.download_feedback_pdf)
        button_layout.addWidget(self.download_pdf_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_feedback()  # Load feedback on initialization

    def load_feedback(self):
        """Load feedback from the database and display them in the table."""
        try:
            with Session(engine) as session:
                feedbacks = self.feedback_view.read_all(db_session=session)
                self.feedback_table.setRowCount(len(feedbacks))
                self.feedback_table.setColumnCount(4)
                self.feedback_table.setHorizontalHeaderLabels(
                    ["ID", "Description", "Status", "Customer Name"]
                )

                for row, feedback in enumerate(feedbacks):
                    customer = session.exec(
                        select(Customer).where(
                            Customer.id == feedback.customer_id
                        )
                    ).first()
                    self.feedback_table.setItem(
                        row, 0, QTableWidgetItem(str(feedback.id))
                    )
                    self.feedback_table.setItem(
                        row, 1, QTableWidgetItem(feedback.description)
                    )
                    self.feedback_table.setItem(
                        row, 2, QTableWidgetItem(feedback.status)
                    )
                    self.feedback_table.setItem(
                        row,
                        3,
                        QTableWidgetItem(customer.name if customer else ""),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load feedback: {e!s}"
            )

    def add_feedback(self):
        """Add a new feedback to the database."""
        dialog = FeedbackDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    customer = session.exec(
                        select(Customer).where(
                            Customer.name == data["customer_name"]
                        )
                    ).first()
                    if not customer:
                        raise ValueError("Customer not found")

                    employee = session.exec(
                        select(Employee).where(
                            Employee.name == data["employee_name"]
                        )
                    ).first()
                    if not employee:
                        raise ValueError("Employee not found")

                    new_feedback = FeedBack(
                        description=data["description"],
                        status=data["status"],
                        customer_id=customer.id,
                        employee_id=employee.id,
                    )
                    self.feedback_view.create(
                        db_session=session, record=new_feedback
                    )
                    QMessageBox.information(
                        self, "Success", "Feedback added successfully!"
                    )
                    self.load_feedback()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add feedback: {e!s}"
                )

    def update_feedback(self):
        """Update an existing feedback."""
        try:
            selected_row = self.feedback_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a feedback to update."
                )
                return

            item = self.feedback_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected feedback ID is invalid."
                )
                return
            feedback_id = item.text()

            dialog = FeedbackDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                with Session(engine) as session:
                    feedback_obj = self.feedback_view.read_by_id(
                        db_session=session, record_id=int(feedback_id)
                    )
                    if feedback_obj:
                        customer = session.exec(
                            select(Customer).where(
                                Customer.name == data["customer_name"]
                            )
                        ).first()
                        if not customer:
                            raise ValueError("Customer not found")

                        employee = session.exec(
                            select(Employee).where(
                                Employee.name == data["employee_name"]
                            )
                        ).first()
                        if not employee:
                            raise ValueError("Employee not found")

                        feedback_obj.description = data["description"]
                        feedback_obj.status = data["status"]
                        feedback_obj.customer_id = customer.id
                        feedback_obj.employee_id = employee.id
                        self.feedback_view.update(
                            db_session=session,
                            record_id=int(feedback_id),
                            record=feedback_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Feedback updated successfully!"
                        )
                        self.load_feedback()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update feedback: {e!s}"
            )

    def delete_feedback(self):
        """Delete a feedback from the database."""
        try:
            selected_row = self.feedback_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a feedback to delete."
                )
                return

            item = self.feedback_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected feedback ID is invalid."
                )
                return
            feedback_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Feedback",
                "Are you sure you want to delete this feedback?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.feedback_view.delete(
                        db_session=session, record_id=int(feedback_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Feedback deleted successfully!"
                    )
                    self.load_feedback()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete feedback: {e!s}"
            )

    def download_feedback_pdf(self):
        """Download feedback as a PDF."""
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("PDF Files (*.pdf)")
            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_path)

                dialog = QPrintDialog(printer, self)
                if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                    self.feedback_table.render(printer)
                    QMessageBox.information(
                        self,
                        "Success",
                        "Feedback PDF downloaded successfully!",
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to download feedback PDF: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = FeedBackGUI()
    window.show()
    app.exec()
