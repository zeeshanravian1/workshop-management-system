"""Payment GUI Module.

Description:
- This module provides the GUI for managing payments.

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
from workshop_management_system.v1.payment.model import Payment
from workshop_management_system.v1.payment.view import PaymentView


class PaymentGUI(QMainWindow):
    """Payment GUI Class.

    Description:
    - This class provides the GUI for managing payments.

    """

    def __init__(self):
        """Initialize the Payment GUI."""
        super().__init__()
        self.setWindowTitle("Payment Management")
        self.setGeometry(100, 100, 800, 600)

        self.payment_view = PaymentView(
            model=Payment
        )  # Initialize PaymentView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Payment table
        self.payment_table = QTableWidget()
        self.payment_table.setSelectionBehavior(
            self.payment_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.payment_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Payments")
        self.load_button.clicked.connect(self.load_payments)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Payment")
        self.add_button.clicked.connect(self.add_payment)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Payment")
        self.update_button.clicked.connect(self.update_payment)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Payment")
        self.delete_button.clicked.connect(self.delete_payment)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_payments()  # Load payments on initialization

    def load_payments(self):
        """Load payments from the database and display them in the table."""
        try:
            with Session(engine) as session:
                payments = self.payment_view.read_all(db_session=session)
                self.payment_table.setRowCount(len(payments))
                self.payment_table.setColumnCount(8)
                self.payment_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Customer ID",
                        "Job Card ID",
                        "Amount",
                        "Payment Date",
                        "Payment Method",
                        "Reference Number",
                        "Status",
                    ]
                )

                for row, payment in enumerate(payments):
                    self.payment_table.setItem(
                        row, 0, QTableWidgetItem(str(payment.payment_id))
                    )
                    self.payment_table.setItem(
                        row, 1, QTableWidgetItem(str(payment.customer_id))
                    )
                    self.payment_table.setItem(
                        row, 2, QTableWidgetItem(str(payment.job_card_id))
                    )
                    self.payment_table.setItem(
                        row, 3, QTableWidgetItem(str(payment.amount))
                    )
                    self.payment_table.setItem(
                        row, 4, QTableWidgetItem(str(payment.payment_date))
                    )
                    self.payment_table.setItem(
                        row, 5, QTableWidgetItem(payment.payment_method)
                    )
                    self.payment_table.setItem(
                        row, 6, QTableWidgetItem(payment.reference_number)
                    )
                    self.payment_table.setItem(
                        row, 7, QTableWidgetItem(payment.status)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load payments: {e!s}"
            )

    def add_payment(self):
        """Add a new payment to the database."""
        try:
            # Get payment details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Add Payment", "Enter Customer ID:"
            )
            if not ok:
                return

            job_card_id, ok = QInputDialog.getInt(
                self, "Add Payment", "Enter Job Card ID:"
            )
            if not ok:
                return

            amount, ok = QInputDialog.getDouble(
                self, "Add Payment", "Enter Amount:"
            )
            if not ok:
                return

            payment_date, ok = QInputDialog.getText(
                self, "Add Payment", "Enter Payment Date (YYYY-MM-DD):"
            )
            if not ok or not payment_date:
                return

            payment_method, ok = QInputDialog.getText(
                self, "Add Payment", "Enter Payment Method:"
            )
            if not ok or not payment_method:
                return

            reference_number, ok = QInputDialog.getText(
                self, "Add Payment", "Enter Reference Number:"
            )
            if not ok or not reference_number:
                return

            status, ok = QInputDialog.getText(
                self, "Add Payment", "Enter Status:"
            )
            if not ok or not status:
                return

            with Session(engine) as session:
                new_payment = Payment(
                    # id is auto-generated by the database
                    customer_id=customer_id,
                    job_card_id=job_card_id,
                    amount=amount,
                    payment_date=datetime.strptime(payment_date, "%Y-%m-%d"),
                    payment_method=payment_method,
                    reference_number=reference_number,
                    status=status,
                )
                self.payment_view.create(
                    db_session=session, record=new_payment
                )
                QMessageBox.information(
                    self, "Success", "Payment added successfully!"
                )
                self.load_payments()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add payment: {e!s}"
            )

    def update_payment(self):
        """Update an existing payment."""
        try:
            selected_row = self.payment_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a payment to update."
                )
                return

            item = self.payment_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected payment ID is invalid."
                )
                return
            payment_id = item.text()

            # Get updated details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Update Payment", "Enter New Customer ID:"
            )
            if not ok:
                return

            job_card_id, ok = QInputDialog.getInt(
                self, "Update Payment", "Enter New Job Card ID:"
            )
            if not ok:
                return

            amount, ok = QInputDialog.getDouble(
                self, "Update Payment", "Enter New Amount:"
            )
            if not ok:
                return

            payment_date, ok = QInputDialog.getText(
                self, "Update Payment", "Enter New Payment Date (YYYY-MM-DD):"
            )
            if not ok or not payment_date:
                return

            payment_method, ok = QInputDialog.getText(
                self, "Update Payment", "Enter New Payment Method:"
            )
            if not ok or not payment_method:
                return

            reference_number, ok = QInputDialog.getText(
                self, "Update Payment", "Enter New Reference Number:"
            )
            if not ok or not reference_number:
                return

            status, ok = QInputDialog.getText(
                self, "Update Payment", "Enter New Status:"
            )
            if not ok or not status:
                return

            with Session(engine) as session:
                payment_obj = self.payment_view.read_by_id(
                    db_session=session, record_id=int(payment_id)
                )
                if payment_obj:
                    payment_obj.customer_id = customer_id
                    payment_obj.job_card_id = job_card_id
                    payment_obj.amount = amount
                    payment_obj.payment_date = datetime.strptime(
                        payment_date, "%Y-%m-%d"
                    )
                    payment_obj.payment_method = payment_method
                    payment_obj.reference_number = reference_number
                    payment_obj.status = status
                    self.payment_view.update(
                        db_session=session,
                        record_id=int(payment_id),
                        record=payment_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Payment updated successfully!"
                    )
                    self.load_payments()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update payment: {e!s}"
            )

    def delete_payment(self):
        """Delete a payment from the database."""
        try:
            selected_row = self.payment_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a payment to delete."
                )
                return

            item = self.payment_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected payment ID is invalid."
                )
                return
            payment_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Payment",
                "Are you sure you want to delete this payment?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.payment_view.delete(
                        db_session=session, record_id=int(payment_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Payment deleted successfully!"
                    )
                    self.load_payments()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete payment: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = PaymentGUI()
    window.show()
    app.exec()
