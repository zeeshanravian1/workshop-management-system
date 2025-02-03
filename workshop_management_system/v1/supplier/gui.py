"""Supplier GUI Module.

Description:
- This module provides the GUI for managing suppliers.

"""

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
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.supplier.model import Supplier
from workshop_management_system.v1.supplier.view import SupplierView


class SupplierDialog(QDialog):
    """Dialog for adding/updating a supplier."""

    def __init__(self, parent=None) -> None:
        """Initialize the Supplier Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Supplier Details")
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

        self.name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.contact_number_input = QLineEdit(self)
        self.address_input = QLineEdit(self)

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Contact Number:", self.contact_number_input)
        self.form_layout.addRow("Address:", self.address_input)

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
            "name": self.name_input.text(),
            "email": self.email_input.text(),
            "contact_number": self.contact_number_input.text(),
            "address": self.address_input.text(),
        }


class SupplierGUI(QWidget):
    """Supplier GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Supplier GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.setStyleSheet("""
            QWidget {
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
                min-width: 125px;
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

        self.supplier_view = SupplierView(model=Supplier)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Supplier Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        main_layout.addWidget(
            back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

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

        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.supplier_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.supplier_table)
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
            ("Load Suppliers", self.load_suppliers),
            ("Add Supplier", self.add_supplier),
            ("Update Supplier", self.update_supplier),
            ("Delete Supplier", self.delete_supplier),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_suppliers()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_suppliers(self) -> None:
        """Load suppliers from the database and display them in the table."""
        try:
            with Session(engine) as session:
                suppliers = self.supplier_view.read_all(db_session=session)
                self.supplier_table.setRowCount(len(suppliers))
                self.supplier_table.setColumnCount(5)
                self.supplier_table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Email", "Contact Number", "Address"]
                )

                for row, supplier in enumerate(suppliers):
                    self.supplier_table.setItem(
                        row, 0, QTableWidgetItem(str(supplier.id))
                    )
                    self.supplier_table.setItem(
                        row, 1, QTableWidgetItem(supplier.name)
                    )
                    self.supplier_table.setItem(
                        row, 2, QTableWidgetItem(supplier.email)
                    )
                    self.supplier_table.setItem(
                        row, 3, QTableWidgetItem(supplier.contact_number)
                    )
                    self.supplier_table.setItem(
                        row, 4, QTableWidgetItem(supplier.address)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load suppliers: {e!s}"
            )

    def add_supplier(self) -> None:
        """Add a new supplier to the database."""
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    new_supplier = Supplier(
                        name=data["name"],
                        email=data["email"],
                        contact_number=data["contact_number"],
                        address=data["address"],
                    )
                    self.supplier_view.create(
                        db_session=session, record=new_supplier
                    )
                    QMessageBox.information(
                        self, "Success", "Supplier added successfully!"
                    )
                    self.load_suppliers()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add supplier: {e!s}"
                )

    def update_supplier(self) -> None:
        """Update an existing supplier."""
        selected_row = self.supplier_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select a supplier to update."
            )
            return

        item = self.supplier_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected supplier ID is invalid."
            )
            return
        supplier_id = item.text()

        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    supplier_obj = self.supplier_view.read_by_id(
                        db_session=session, record_id=int(supplier_id)
                    )
                    if supplier_obj:
                        supplier_obj.name = data["name"]
                        supplier_obj.email = data["email"]
                        supplier_obj.contact_number = data["contact_number"]
                        supplier_obj.address = data["address"]
                        self.supplier_view.update(
                            db_session=session,
                            record_id=int(supplier_id),
                            record=supplier_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Supplier updated successfully!"
                        )
                        self.load_suppliers()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update supplier: {e!s}"
                )

    def delete_supplier(self) -> None:
        """Delete a supplier from the database."""
        try:
            selected_row = self.supplier_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a supplier to delete."
                )
                return

            item = self.supplier_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected supplier ID is invalid."
                )
                return
            supplier_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Supplier",
                "Are you sure you want to delete this supplier?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.supplier_view.delete(
                        db_session=session, record_id=int(supplier_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Supplier deleted successfully!"
                    )
                    self.load_suppliers()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete supplier: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = SupplierGUI()
    window.show()
    app.exec()
