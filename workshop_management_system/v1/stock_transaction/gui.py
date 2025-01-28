"""Stock Transaction GUI Module.

Description:
- This module provides the GUI for managing stock transactions.
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.stock_transaction.model import (
    StockTransaction,
)
from workshop_management_system.v1.stock_transaction.view import (
    StockTransactionView,
)


class AddEditStockTransactionDialog(QDialog):
    """Dialog for adding/editing stock transactions."""

    def __init__(self, parent=None, transaction=None) -> None:
        """Initialize dialog."""
        super().__init__(parent)
        self.setWindowTitle("Stock Transaction")
        self.transaction = transaction
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QFormLayout()

        # Inventory ID
        self.inventory_id = QLineEdit()
        if self.transaction:
            self.inventory_id.setText(str(self.transaction.inventory_id))
        layout.addRow("Inventory ID:", self.inventory_id)

        # Transaction Type
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["IN", "OUT"])
        if self.transaction:
            self.transaction_type.setCurrentText(
                self.transaction.transaction_type
            )
        layout.addRow("Transaction Type:", self.transaction_type)

        # Quantity
        self.quantity = QSpinBox()
        self.quantity.setRange(-10000, 10000)
        if self.transaction:
            self.quantity.setValue(self.transaction.quantity)
        layout.addRow("Quantity:", self.quantity)

        # Transaction Date
        self.transaction_date = QDateTimeEdit()
        self.transaction_date.setCalendarPopup(True)
        self.transaction_date.setDateTime(
            self.transaction.transaction_date
            if self.transaction
            else datetime.now()
        )
        layout.addRow("Transaction Date:", self.transaction_date)

        # Job Card ID (Optional)
        self.job_card_id = QLineEdit()
        if self.transaction and self.transaction.job_card_id:
            self.job_card_id.setText(str(self.transaction.job_card_id))
        layout.addRow("Job Card ID (Optional):", self.job_card_id)

        # Remarks
        self.remarks = QLineEdit()
        if self.transaction:
            self.remarks.setText(self.transaction.remarks)
        layout.addRow("Remarks:", self.remarks)

        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

    def get_data(self) -> dict:  # -> dict[str, Any]:
        """Get dialog data."""
        job_card_id_text = self.job_card_id.text()
        return {
            "inventory_id": int(self.inventory_id.text()),
            "transaction_type": self.transaction_type.currentText(),
            "quantity": self.quantity.value(),
            "transaction_date": (
                self.transaction_date.dateTime().toPyDateTime()
            ),
            "job_card_id": int(job_card_id_text) if job_card_id_text else None,
            "remarks": self.remarks.text(),
        }


class StockTransactionGUI(QMainWindow):
    """Stock Transaction GUI Class."""

    def __init__(self) -> None:
        """Initialize the Stock Transaction GUI."""
        super().__init__()
        self.setWindowTitle("Stock Transaction Management")
        self.setGeometry(100, 100, 1000, 600)

        self.transaction_view = StockTransactionView(model=StockTransaction)

        self.main_layout = QVBoxLayout()

        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setSelectionBehavior(
            self.transaction_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.transaction_table)

        # Buttons
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Transactions")
        self.load_button.clicked.connect(self.load_transactions)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Transaction")
        self.update_button.clicked.connect(self.update_transaction)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Transaction")
        self.delete_button.clicked.connect(self.delete_transaction)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_transactions()

    def load_transactions(self) -> None:
        """Load transactions from database."""
        try:
            with Session(engine) as session:
                transactions = self.transaction_view.read_all(
                    db_session=session
                )
                self.transaction_table.setRowCount(len(transactions))
                self.transaction_table.setColumnCount(7)
                self.transaction_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Inventory ID",
                        "Type",
                        "Quantity",
                        "Date",
                        "Job Card ID",
                        "Remarks",
                    ]
                )

                for row, trans in enumerate(transactions):
                    self.transaction_table.setItem(
                        row, 0, QTableWidgetItem(str(trans.id))
                    )
                    self.transaction_table.setItem(
                        row, 1, QTableWidgetItem(str(trans.inventory_id))
                    )
                    self.transaction_table.setItem(
                        row, 2, QTableWidgetItem(trans.transaction_type)
                    )
                    self.transaction_table.setItem(
                        row, 3, QTableWidgetItem(str(trans.quantity))
                    )
                    self.transaction_table.setItem(
                        row, 4, QTableWidgetItem(str(trans.transaction_date))
                    )
                    self.transaction_table.setItem(
                        row, 5, QTableWidgetItem(str(trans.job_card_id))
                    )
                    self.transaction_table.setItem(
                        row, 6, QTableWidgetItem(trans.remarks)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load transactions: {e!s}"
            )

    def add_transaction(self) -> None:
        """Add a new transaction."""
        try:
            dialog = AddEditStockTransactionDialog(self)
            if dialog.exec():
                with Session(engine) as session:
                    new_transaction = StockTransaction(**dialog.get_data())
                    self.transaction_view.create(
                        db_session=session, record=new_transaction
                    )
                    QMessageBox.information(
                        self, "Success", "Transaction added successfully!"
                    )
                    self.load_transactions()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add transaction: {e!s}"
            )

    def update_transaction(self) -> None:
        """Update existing transaction."""
        try:
            selected_row = self.transaction_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a transaction to update."
                )
                return

            transaction_id = int(
                self.transaction_table.item(selected_row, 0).text()
            )

            with Session(engine) as session:
                transaction = self.transaction_view.read_by_id(
                    db_session=session, record_id=transaction_id
                )
                if transaction:
                    dialog = AddEditStockTransactionDialog(self, transaction)
                    if dialog.exec():
                        for key, value in dialog.get_data().items():
                            setattr(transaction, key, value)
                        self.transaction_view.update(
                            db_session=session,
                            record_id=transaction_id,
                            record=transaction,
                        )
                        QMessageBox.information(
                            self,
                            "Success",
                            "Transaction updated successfully!",
                        )
                        self.load_transactions()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update transaction: {e!s}"
            )

    def delete_transaction(self) -> None:
        """Delete a transaction."""
        try:
            selected_row = self.transaction_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a transaction to delete."
                )
                return

            transaction_id = int(
                self.transaction_table.item(selected_row, 0).text()
            )

            confirmation = QMessageBox.question(
                self,
                "Delete Transaction",
                "Are you sure you want to delete this transaction?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.transaction_view.delete(
                        db_session=session, record_id=transaction_id
                    )
                    QMessageBox.information(
                        self, "Success", "Transaction deleted successfully!"
                    )
                    self.load_transactions()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete transaction: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = StockTransactionGUI()
    window.show()
    app.exec()
