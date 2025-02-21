"""Supplier GUI Module.

Description:
- This module provides the GUI for managing suppliers.

"""

import re

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
    QHeaderView,  # Add this
    QLabel,
    QLineEdit,
    QMenu,  # Add this
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,  # Add this
    QVBoxLayout,
    QWidget,
)

from workshop_management_system.database.session import get_session
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
        # Update pagination to match BaseView pattern
        self.current_page = 1
        self.page_size = 15
        self.supplier_view = SupplierView(model=Supplier)

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
        """Filter suppliers based on search criteria."""
        self.current_page = 1
        self.load_suppliers()

    def load_suppliers(self, refresh_all=True) -> None:
        """Load suppliers using backend pagination."""
        try:
            search_text = self.search_input.text()
            search_field = (
                self.search_criteria.currentText().lower()
                if search_text
                else None
            )

            with get_session() as session:
                result = self.supplier_view.read_all(
                    db_session=session,
                    page=self.current_page,
                    limit=self.page_size,
                    search_by=search_field,
                    search_query=search_text,
                )

                # Update pagination controls
                self.prev_button.setEnabled(
                    result.previous_record_id is not None
                )
                self.next_button.setEnabled(result.next_record_id is not None)
                self._update_table_data(result.records)
                self.update_pagination_buttons(result.total_pages)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load suppliers: {e!s}"
            )

    def add_supplier(self) -> None:
        """Add supplier using BaseView."""
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                with get_session() as session:
                    new_supplier = Supplier(**dialog.get_data())
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
        """Update supplier using BaseView."""
        try:
            selected_row = self.supplier_table.currentRow()
            if selected_row <= 0:
                QMessageBox.warning(
                    self, "Warning", "Please select a supplier to update."
                )
                return

            supplier_id = int(self.supplier_table.item(selected_row, 0).text())

            with get_session() as session:
                supplier = self.supplier_view.read_by_id(
                    db_session=session, record_id=supplier_id
                )
                if not supplier:
                    QMessageBox.warning(self, "Error", "Supplier not found.")
                    return

                dialog = SupplierDialog(
                    self,
                    {
                        "name": supplier.name,
                        "email": supplier.email,
                        "contact_number": supplier.contact_no,
                        "address": supplier.address,
                    },
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_supplier = Supplier(**dialog.get_data())
                    self.supplier_view.update_by_id(
                        db_session=session,
                        record_id=supplier_id,
                        record=updated_supplier,
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
        """Delete supplier using BaseView."""
        try:
            selected_row = self.supplier_table.currentRow()
            if selected_row <= 0:
                QMessageBox.warning(
                    self, "Warning", "Please select a supplier to delete."
                )
                return

            supplier_id = int(self.supplier_table.item(selected_row, 0).text())

            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this supplier?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                with get_session() as session:
                    if self.supplier_view.delete_by_id(
                        db_session=session, record_id=supplier_id
                    ):
                        QMessageBox.information(
                            self, "Success", "Supplier deleted successfully!"
                        )
                        self.load_suppliers()
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Supplier not found!"
                        )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete supplier: {e!s}"
            )

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
        """Load the next page of suppliers."""
        if self.pagination["next_record_id"] is not None:
            self.pagination["current_page"] += 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_suppliers(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of suppliers."""
        if self.pagination["previous_record_id"] is not None:
            self.pagination["current_page"] -= 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_suppliers(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if (
            1 <= page_number <= self.pagination["total_pages"]
            and page_number != self.pagination["current_page"]
        ):
            self.pagination["current_page"] = page_number
            self.current_page = page_number  # Keep in sync
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

    def _update_table_data(self, records):
        """Update table data while preserving table properties."""
        self.supplier_table.setRowCount(len(records) + 1)  # +1 for header
        self.supplier_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Name", "Email", "Contact Number", "Address"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.supplier_table.setItem(0, col, item)

        # Populate data
        for row, supplier in enumerate(records, start=1):
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

        # Maintain table appearance
        self.supplier_table.resizeColumnsToContents()
        self.supplier_table.horizontalHeader().setStretchLastSection(True)
        self.supplier_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.supplier_table.rowCount()):
            self.supplier_table.setRowHeight(row, row_height)


if __name__ == "__main__":
    app = QApplication([])
    window = SupplierGUI()
    window.show()
    app.exec()
