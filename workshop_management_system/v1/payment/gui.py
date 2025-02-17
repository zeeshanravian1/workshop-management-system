"""Payment GUI Module.

Description:
- This module provides the GUI for managing payments.

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


class PaymentGUI(QWidget):
    """Payment GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Payment GUI."""
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
                border: 1px solid black;  /* Add border to the table */
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: green;
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

        self.payment_view = PaymentView(model=Payment)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Payment Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search payments...")
        self.search_input.textChanged.connect(self.search_payments)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Customer ID", "Job Card ID", "Payment Method", "Status"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_payments)

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

        # Payment table
        self.payment_table = QTableWidget()
        self.payment_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.payment_table.setAlternatingRowColors(True)
        self.payment_table.setStyleSheet("""
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
                background-color: green;
                color: white;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: none;
            }
        """)
        self.payment_table.verticalHeader().setVisible(False)
        self.payment_table.horizontalHeader().setVisible(False)
        self.payment_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.payment_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.payment_table.horizontalHeader().setStretchLastSection(True)
        self.payment_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_payments(self) -> None:
        """Load payments from the database and display them in the table."""
        try:
            with Session(engine) as session:
                payments = self.payment_view.read_all(db_session=session)
                self.payment_table.setRowCount(len(payments) + 1)
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

                # Set column names in the first row
                column_names = [
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
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.payment_table.setItem(0, col, item)

                # Set the height of the first row
                self.payment_table.setRowHeight(0, 40)

                for row, payment in enumerate(payments, start=1):
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

                # Adjust column widths
                self.payment_table.resizeColumnsToContents()
                self.payment_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.payment_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
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

    def search_payments(self) -> None:
        """Filter payments based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.payment_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "customer id":
                    cell_text = self.payment_table.item(row, 1)
                elif criteria == "job card id":
                    cell_text = self.payment_table.item(row, 2)
                elif criteria == "payment method":
                    cell_text = self.payment_table.item(row, 7)
                elif criteria == "status":
                    cell_text = self.payment_table.item(row, 9)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.payment_table.setRowHidden(row, not show_row)


if __name__ == "__main__":
    app = QApplication([])
    window = PaymentGUI()
    window.show()
    app.exec()
