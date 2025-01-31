"""Payment GUI Module.

Description:
- This module provides the GUI for managing payments.

"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.jobcard.model import JobCard
from workshop_management_system.v1.payment.model import Payment
from workshop_management_system.v1.payment.view import PaymentView


class PaymentDialog(QDialog):
    """Dialog for adding/updating a payment."""

    def __init__(self, parent=None) -> None:
        """Initialize the Payment Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Payment Details")
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

        self.customer_id_input = QLineEdit(self)
        self.job_card_id_input = QLineEdit(self)
        self.amount_input = QLineEdit(self)
        self.payment_date_input = QLineEdit(self)
        self.payment_method_input = QLineEdit(self)
        self.reference_number_input = QLineEdit(self)
        self.status_input = QLineEdit(self)
        self.credit_input = QLineEdit(self)
        self.balance_input = QLineEdit(self)

        self.form_layout.addRow("Customer ID:", self.customer_id_input)
        self.form_layout.addRow("Job Card ID:", self.job_card_id_input)
        self.form_layout.addRow("Amount:", self.amount_input)
        self.form_layout.addRow(
            "Payment Date (YYYY-MM-DD):", self.payment_date_input
        )
        self.form_layout.addRow("Payment Method:", self.payment_method_input)
        self.form_layout.addRow(
            "Reference Number:", self.reference_number_input
        )
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow("Credit:", self.credit_input)
        self.form_layout.addRow("Balance:", self.balance_input)

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
            "customer_id": int(self.customer_id_input.text()),
            "job_card_id": int(self.job_card_id_input.text()),
            "amount": float(self.amount_input.text()),
            "payment_date": self.payment_date_input.text(),
            "payment_method": self.payment_method_input.text(),
            "reference_number": self.reference_number_input.text(),
            "status": self.status_input.text(),
            "credit": float(self.credit_input.text()),
            "balance": float(self.balance_input.text()),
        }


class PaymentGUI(QMainWindow):
    """Payment GUI Class.

    Description:
    - This class provides the GUI for managing payments.

    """

    def __init__(self) -> None:
        """Initialize the Payment GUI."""
        super().__init__()
        self.setWindowTitle("Payment Management")
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

        self.payment_view = PaymentView(model=Payment)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Payment Management")
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

        # Payment table
        self.payment_table = QTableWidget()
        self.payment_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.payment_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.payment_table)
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
            ("Load Payments", self.load_payments),
            ("Add Payment", self.add_payment),
            ("Update Payment", self.update_payment),
            ("Delete Payment", self.delete_payment),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_payments()

    def load_payments(self) -> None:
        """Load payments from the database and display them in the table."""
        try:
            with Session(engine) as session:
                payments = self.payment_view.read_all(db_session=session)
                self.payment_table.setRowCount(len(payments))
                self.payment_table.setColumnCount(10)
                self.payment_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Customer ID",
                        "Job Card ID",
                        "Amount",
                        "Credit",
                        "Balance",
                        "Payment Date",
                        "Payment Method",
                        "Reference Number",
                        "Status",
                    ]
                )

                for row, payment in enumerate(payments):
                    self.payment_table.setItem(
                        row, 0, QTableWidgetItem(str(payment.id))
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
                        row, 4, QTableWidgetItem(str(payment.credit))
                    )
                    self.payment_table.setItem(
                        row, 5, QTableWidgetItem(str(payment.balance))
                    )
                    self.payment_table.setItem(
                        row, 6, QTableWidgetItem(str(payment.payment_date))
                    )
                    self.payment_table.setItem(
                        row, 7, QTableWidgetItem(payment.payment_method)
                    )
                    self.payment_table.setItem(
                        row, 8, QTableWidgetItem(payment.reference_number)
                    )
                    self.payment_table.setItem(
                        row, 9, QTableWidgetItem(payment.status)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load payments: {e!s}"
            )

    def add_payment(self) -> None:
        """Add a new payment to the database."""
        dialog = PaymentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    customer = session.exec(
                        select(Customer).where(
                            Customer.id == data["customer_id"]
                        )
                    ).first()
                    if not customer:
                        raise ValueError("Customer not found")

                    job_card = session.exec(
                        select(JobCard).where(
                            JobCard.id == data["job_card_id"]
                        )
                    ).first()
                    if not job_card:
                        raise ValueError("Job Card not found")

                    new_payment = Payment(
                        customer_id=data["customer_id"],
                        job_card_id=data["job_card_id"],
                        amount=data["amount"],
                        credit=data["credit"],
                        balance=data["balance"],
                        payment_date=datetime.strptime(
                            data["payment_date"], "%Y-%m-%d"
                        ),
                        payment_method=data["payment_method"],
                        reference_number=data["reference_number"],
                        status=data["status"],
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

    def update_payment(self) -> None:
        """Update an existing payment."""
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

        dialog = PaymentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    payment_obj = self.payment_view.read_by_id(
                        db_session=session, record_id=int(payment_id)
                    )
                    if payment_obj:
                        payment_obj.customer_id = data["customer_id"]
                        payment_obj.job_card_id = data["job_card_id"]
                        payment_obj.amount = data["amount"]
                        payment_obj.credit = data["credit"]
                        payment_obj.balance = data["balance"]
                        payment_obj.payment_date = datetime.strptime(
                            data["payment_date"], "%Y-%m-%d"
                        )
                        payment_obj.payment_method = data["payment_method"]
                        payment_obj.reference_number = data["reference_number"]
                        payment_obj.status = data["status"]
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

    def delete_payment(self) -> None:
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
