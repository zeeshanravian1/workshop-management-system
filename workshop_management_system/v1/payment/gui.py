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
    QTableWidgetItem,  # Add this import
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
        # Add pagination dictionary to match base model
        self.pagination = {
            "current_page": 1,
            "limit": 15,
            "total_pages": 0,
            "total_records": 0,
            "next_record_id": None,
            "previous_record_id": None,
            "records": [],
        }
        # Keep compatibility properties
        self.page_size = self.pagination["limit"]
        self.current_page = self.pagination["current_page"]
        self.all_payments = []
        self.filtered_payments = []

        # Update theme to match other GUIs
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: skyblue;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                margin: 0px;
            }
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
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
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
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

        # Add pagination frame
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setSpacing(5)

        # Previous button
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Page number buttons container
        self.page_buttons_layout = QHBoxLayout()
        self.page_buttons_layout.setSpacing(5)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addLayout(self.page_buttons_layout)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(pagination_frame)

        self.load_payments()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_payments(self, refresh_all=True) -> None:
        """Load payments with pagination."""
        try:
            with Session(engine) as session:
                if refresh_all:
                    self.all_payments = self.payment_view.read_all(
                        db_session=session
                    )
                    self.filtered_payments = self.all_payments.copy()

                total_records = len(self.filtered_payments)
                total_pages = (
                    total_records + self.pagination["limit"] - 1
                ) // self.pagination["limit"]

                # Update pagination state
                self.pagination.update(
                    {
                        "total_records": total_records,
                        "total_pages": total_pages,
                    }
                )

                # Calculate page data
                start_idx = (
                    self.pagination["current_page"] - 1
                ) * self.pagination["limit"]
                end_idx = start_idx + self.pagination["limit"]
                current_page_records = self.filtered_payments[
                    start_idx:end_idx
                ]
                self.pagination["records"] = current_page_records

                # Update next/previous record IDs
                if end_idx < total_records:
                    self.pagination["next_record_id"] = self.filtered_payments[
                        end_idx
                    ].id
                else:
                    self.pagination["next_record_id"] = None

                if start_idx > 0:
                    self.pagination["previous_record_id"] = (
                        self.filtered_payments[start_idx - 1].id
                    )
                else:
                    self.pagination["previous_record_id"] = None

                # Update table content
                self._update_table_data(current_page_records)

                # Update pagination UI
                self.update_pagination_buttons(total_pages)
                self.prev_button.setEnabled(
                    self.pagination["previous_record_id"] is not None
                )
                self.next_button.setEnabled(
                    self.pagination["next_record_id"] is not None
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
        """Filter payments based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        # Filter all payments
        self.filtered_payments = self.all_payments.copy()
        if search_text:
            self.filtered_payments = [
                payment
                for payment in self.all_payments
                if (
                    (
                        criteria == "customer id"
                        and search_text in str(payment.customer_id).lower()
                    )
                    or (
                        criteria == "job card id"
                        and search_text in str(payment.job_card_id).lower()
                    )
                    or (
                        criteria == "payment method"
                        and search_text in payment.payment_method.lower()
                    )
                    or (
                        criteria == "status"
                        and search_text in payment.status.lower()
                    )
                )
            ]

        # Reset pagination
        self.pagination["current_page"] = 1
        self.current_page = 1  # Keep in sync
        self.pagination["total_records"] = len(self.filtered_payments)

        # Reload table with filtered data
        self.load_payments(refresh_all=False)

    # Add these new pagination methods
    def update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        # Clear existing buttons
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_page = self.pagination["current_page"]

        # Always show first page
        self.add_page_button(1)

        if total_pages > 7:
            # Show ellipsis after first page if needed
            if current_page > 3:
                self.page_buttons_layout.addWidget(self._create_ellipsis())

            # Show pages around current page
            if current_page <= 3:
                # Near start - show first few pages
                for page in range(2, 6):
                    self.add_page_button(page)
            elif current_page >= total_pages - 2:
                # Near end - show last few pages
                for page in range(total_pages - 4, total_pages):
                    self.add_page_button(page)
            else:
                # In middle - show pages around current
                for page in range(current_page - 2, current_page + 3):
                    if 1 < page < total_pages:
                        self.add_page_button(page)

            # Show ellipsis before last page if needed
            if current_page < total_pages - 3:
                self.page_buttons_layout.addWidget(self._create_ellipsis())
        else:
            # For small number of pages, show all pages
            for page in range(2, total_pages + 1):
                self.add_page_button(page)

        # Always show last page if more than one page
        if total_pages > 1:
            self.add_page_button(total_pages)

    def _create_ellipsis(self):
        """Create ellipsis button for pagination."""
        ellipsis = QPushButton("...")
        ellipsis.setEnabled(False)
        ellipsis.setFixedSize(40, 40)
        ellipsis.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-weight: bold;
                min-width: 40px;
            }
        """)
        return ellipsis

    def add_page_button(self, page_num: int) -> None:
        """Add a single page button."""
        button = QPushButton(str(page_num))
        button.setFixedSize(40, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumWidth(40)
        button.setMaximumWidth(40)

        if page_num == self.pagination["current_page"]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: skyblue;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    min-width: 40px;
                    max-width: 40px;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    min-width: 40px;
                    max-width: 40px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

        button.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_buttons_layout.addWidget(button)

    def next_page(self) -> None:
        """Load the next page of payments."""
        if self.pagination["next_record_id"] is not None:
            self.pagination["current_page"] += 1
            self.current_page = self.pagination["current_page"]
            self.load_payments(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of payments."""
        if self.pagination["previous_record_id"] is not None:
            self.pagination["current_page"] -= 1
            self.current_page = self.pagination["current_page"]
            self.load_payments(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if (
            1 <= page_number <= self.pagination["total_pages"]
            and page_number != self.pagination["current_page"]
        ):
            self.pagination["current_page"] = page_number
            self.current_page = page_number
            self.load_payments(refresh_all=False)

    def _update_table_data(self, records):
        """Update table data while preserving table properties."""
        self.payment_table.setRowCount(len(records) + 1)  # +1 for header
        self.payment_table.setColumnCount(10)

        # Set headers
        headers = [
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
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.payment_table.setItem(0, col, item)

        # Populate data
        for row, payment in enumerate(records, start=1):
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

        # Maintain table appearance
        self.payment_table.resizeColumnsToContents()
        self.payment_table.horizontalHeader().setStretchLastSection(True)
        self.payment_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.payment_table.rowCount()):
            self.payment_table.setRowHeight(row, row_height)


if __name__ == "__main__":
    app = QApplication([])
    window = PaymentGUI()
    window.show()
    app.exec()
