"""Supplier GUI Module.

Description:
- This module provides the GUI for managing suppliers.

"""

import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QComboBox  # Add this import
from PyQt6.QtWidgets import (
    QApplication,
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
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.supplier.model import Supplier
from workshop_management_system.v1.supplier.view import SupplierView


class SupplierDialog(QDialog):
    """Dialog for adding/updating a supplier."""

    def __init__(self, parent=None, initial_data=None) -> None:
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

        if initial_data:
            self.name_input.setText(initial_data.get("name", ""))
            self.email_input.setText(initial_data.get("email", ""))
            self.contact_number_input.setText(
                initial_data.get("contact_number", "")
            )
            self.address_input.setText(initial_data.get("address", ""))

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

    def accept(self) -> None:
        """Validate the input fields before accepting the dialog."""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email is required.")
            return
        if not re.match(
            r"[^@]+@[^@]+\.[^@]+", self.email_input.text().strip()
        ):
            QMessageBox.warning(
                self, "Validation Error", "Invalid email format."
            )
            return
        if not self.contact_number_input.text().strip():
            QMessageBox.warning(
                self, "Validation Error", "Contact number is required."
            )
            return
        if not re.match(
            r"^\+?\d{10,15}$", self.contact_number_input.text().strip()
        ):
            QMessageBox.warning(
                self, "Validation Error", "Invalid contact number format."
            )
            return
        if not self.address_input.text().strip():
            QMessageBox.warning(
                self, "Validation Error", "Address is required."
            )
            return
        super().accept()


class SupplierGUI(QWidget):
    """Supplier GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Supplier GUI."""
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
                background-color: #87CEEB;
                color: white;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                min-width: 125px;
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
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #87CEEB;  /* Highlight color for selected row */
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

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search suppliers...")
        self.search_input.textChanged.connect(self.search_suppliers)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Name", "Email", "Contact Number", "Address"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_suppliers)

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

        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows  # Enable row selection
        )
        self.supplier_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection  # Allow single row selection
        )
        self.supplier_table.setAlternatingRowColors(True)
        self.supplier_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid black;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #87CEEB;  /* Highlight color for selected row */
                color: white;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: none;
            }
        """)
        self.supplier_table.verticalHeader().setVisible(False)
        self.supplier_table.horizontalHeader().setVisible(False)
        self.supplier_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.supplier_table.horizontalHeader().setStretchLastSection(True)
        self.supplier_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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

    def search_suppliers(self) -> None:
        """Filter suppliers based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.supplier_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "name":
                    cell_text = self.supplier_table.item(row, 1)
                elif criteria == "email":
                    cell_text = self.supplier_table.item(row, 2)
                elif criteria == "contact number":
                    cell_text = self.supplier_table.item(row, 3)
                elif criteria == "address":
                    cell_text = self.supplier_table.item(row, 4)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.supplier_table.setRowHidden(row, not show_row)

    def load_suppliers(self) -> None:
        """Load suppliers from the database and display them in the table."""
        try:
            with Session(engine) as session:
                suppliers = self.supplier_view.read_all(db_session=session)
                self.supplier_table.setRowCount(len(suppliers) + 1)
                self.supplier_table.setColumnCount(5)
                self.supplier_table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Email", "Contact Number", "Address"]
                )

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Name",
                    "Email",
                    "Contact Number",
                    "Address",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.supplier_table.setItem(0, col, item)

                # Set the height of the first row
                self.supplier_table.setRowHeight(0, 40)

                for row, supplier in enumerate(suppliers, start=1):
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

                # Adjust column widths
                self.supplier_table.resizeColumnsToContents()
                self.supplier_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.supplier_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )

                # After loading suppliers, apply any existing search filter
                self.search_suppliers()

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

        try:
            with Session(engine) as session:
                supplier_obj = self.supplier_view.read_by_id(
                    db_session=session, record_id=int(supplier_id)
                )
                if supplier_obj:
                    initial_data = {
                        "name": supplier_obj.name,
                        "email": supplier_obj.email,
                        "contact_number": supplier_obj.contact_number,
                        "address": supplier_obj.address,
                    }
                    dialog = SupplierDialog(self, initial_data=initial_data)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        data = dialog.get_data()
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
