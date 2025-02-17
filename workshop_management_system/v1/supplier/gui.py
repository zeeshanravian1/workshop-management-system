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
    QSizePolicy,
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
        self.page_size = 15
        self.current_page = 1
        self.total_records = 0
        self.all_suppliers = []
        self.filtered_suppliers = []
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

        # Search Section (add this after header_layout)
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
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_frame.setMinimumHeight(300)
        table_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.supplier_table.setAlternatingRowColors(True)
        self.supplier_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.supplier_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
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
        self.supplier_table.verticalHeader().setVisible(False)
        self.supplier_table.horizontalHeader().setVisible(False)
        self.supplier_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.supplier_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.supplier_table.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.supplier_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.supplier_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.supplier_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.supplier_table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        table_layout.addWidget(self.supplier_table)
        main_layout.addWidget(table_frame, 1)

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

        # Pagination Frame
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

        self.load_suppliers()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def search_suppliers(self) -> None:
        """Filter suppliers based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        self.filtered_suppliers = self.all_suppliers.copy()
        if search_text:
            self.filtered_suppliers = [
                supplier
                for supplier in self.all_suppliers
                if (
                    (
                        criteria == "name"
                        and search_text in supplier.name.lower()
                    )
                    or (
                        criteria == "email"
                        and search_text in supplier.email.lower()
                    )
                    or (
                        criteria == "contact number"
                        and search_text in supplier.contact_number.lower()
                    )
                    or (
                        criteria == "address"
                        and search_text in supplier.address.lower()
                    )
                )
            ]

        self.current_page = 1
        self.total_records = len(self.filtered_suppliers)
        self.load_suppliers(refresh_all=False)

    def load_suppliers(self, refresh_all=True) -> None:
        """Load suppliers with pagination."""
        try:
            with Session(engine) as session:
                if refresh_all:
                    self.all_suppliers = self.supplier_view.read_all(
                        db_session=session
                    )
                    self.filtered_suppliers = self.all_suppliers.copy()
                    self.total_records = len(self.all_suppliers)

                total_pages = (
                    self.total_records + self.page_size - 1
                ) // self.page_size
                offset = (self.current_page - 1) * self.page_size
                current_page_suppliers = self.filtered_suppliers[
                    offset : offset + self.page_size
                ]

                self.supplier_table.setRowCount(
                    len(current_page_suppliers) + 1
                )
                self.supplier_table.setColumnCount(5)
                self.supplier_table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Email", "Contact Number", "Address"]
                )

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

                self.supplier_table.setRowHeight(0, 40)

                for row, supplier in enumerate(
                    current_page_suppliers, start=1
                ):
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

                self.supplier_table.resizeColumnsToContents()
                self.supplier_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.supplier_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )

                row_height = 40
                for row in range(self.supplier_table.rowCount()):
                    self.supplier_table.setRowHeight(row, row_height)

                visible_rows = min(
                    len(current_page_suppliers) + 1, self.page_size + 1
                )
                table_height = (row_height * visible_rows) + 20
                self.supplier_table.setMinimumHeight(0)
                self.supplier_table.setMaximumHeight(
                    16777215
                )  # Qt's maximum value

                self.update_pagination_buttons(total_pages)
                self.prev_button.setEnabled(self.current_page > 1)
                self.next_button.setEnabled(self.current_page < total_pages)

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

    def update_pagination_buttons(self, total_pages: int) -> None:
        """Update the pagination buttons."""
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        max_visible_pages = 7
        if total_pages <= max_visible_pages:
            for page in range(1, total_pages + 1):
                self.add_page_button(page)
        else:
            for page in range(1, 4):
                self.add_page_button(page)

            if self.current_page > 4:
                ellipsis = QPushButton("...")
                ellipsis.setEnabled(False)
                ellipsis.setStyleSheet("background: none; border: none;")
                self.page_buttons_layout.addWidget(ellipsis)

            if 4 < self.current_page < total_pages - 3:
                self.add_page_button(self.current_page)

            if self.current_page < total_pages - 3:
                ellipsis = QPushButton("...")
                ellipsis.setEnabled(False)
                ellipsis.setStyleSheet("background: none; border: none;")
                self.page_buttons_layout.addWidget(ellipsis)

            for page in range(total_pages - 2, total_pages + 1):
                self.add_page_button(page)

    def add_page_button(self, page_num: int) -> None:
        """Add a single page button."""
        button = QPushButton(str(page_num))
        button.setFixedSize(40, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if page_num == self.current_page:
            button.setStyleSheet("""
                QPushButton {
                    background-color: skyblue;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

        button.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_buttons_layout.addWidget(button)

    def next_page(self) -> None:
        """Load the next page of suppliers."""
        total_pages = (
            self.total_records + self.page_size - 1
        ) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_suppliers(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of suppliers."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_suppliers(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if page_number != self.current_page:
            self.current_page = page_number
            self.load_suppliers(refresh_all=False)

    def show_context_menu(self, position):
        """Show context menu for table row."""
        row = self.supplier_table.rowAt(position.y())
        if row > 0:  # Skip header row
            self.supplier_table.selectRow(row)
            context_menu = QMenu(self)
            context_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 25px;
                    color: black;
                    border-radius: 4px;
                    margin: 2px 5px;
                }
                QMenu::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background: #cccccc;
                    margin: 5px 0px;
                }
            """)

            update_action = context_menu.addAction("✏️ Update")
            update_action.setStatusTip("Update selected supplier")

            context_menu.addSeparator()

            delete_action = context_menu.addAction("🗑️ Delete")
            delete_action.setStatusTip("Delete selected supplier")

            action = context_menu.exec(
                self.supplier_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_supplier()
            elif action == delete_action:
                self.delete_supplier()


if __name__ == "__main__":
    app = QApplication([])
    window = SupplierGUI()
    window.show()
    app.exec()
