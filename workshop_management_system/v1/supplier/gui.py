"""Supplier GUI Module.

Description:
- This module provides the GUI for managing suppliers.
"""

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
from workshop_management_system.v1.supplier.model import Supplier
from workshop_management_system.v1.supplier.view import SupplierView


class SupplierGUI(QMainWindow):
    """Supplier GUI Class."""

    def __init__(self) -> None:
        """Initialize the Supplier GUI."""
        super().__init__()
        self.setWindowTitle("Supplier Management")
        self.setGeometry(100, 100, 800, 600)

        self.supplier_view = SupplierView(model=Supplier)

        self.main_layout = QVBoxLayout()

        # Supplier table
        self.supplier_table = QTableWidget()
        self.supplier_table.setSelectionBehavior(
            self.supplier_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.supplier_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Suppliers")
        self.load_button.clicked.connect(self.load_suppliers)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Supplier")
        self.add_button.clicked.connect(self.add_supplier)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Supplier")
        self.update_button.clicked.connect(self.update_supplier)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Supplier")
        self.delete_button.clicked.connect(self.delete_supplier)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_suppliers()

    def load_suppliers(self) -> None:
        """Load suppliers from database."""
        try:
            with Session(engine) as session:
                suppliers = self.supplier_view.read_all(db_session=session)
                self.supplier_table.setRowCount(len(suppliers))
                self.supplier_table.setColumnCount(4)
                self.supplier_table.setHorizontalHeaderLabels(
                    ["ID", "Name", "Contact Number", "Address"]
                )

                for row, supplier in enumerate(suppliers):
                    self.supplier_table.setItem(
                        row, 0, QTableWidgetItem(str(supplier.id))
                    )
                    self.supplier_table.setItem(
                        row, 1, QTableWidgetItem(supplier.name)
                    )
                    self.supplier_table.setItem(
                        row, 2, QTableWidgetItem(supplier.contact_number)
                    )
                    self.supplier_table.setItem(
                        row, 3, QTableWidgetItem(supplier.address)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load suppliers: {e!s}"
            )

    def add_supplier(self) -> None:
        """Add a new supplier."""
        try:
            name, ok = QInputDialog.getText(
                self, "Add Supplier", "Enter Supplier Name:"
            )
            if not ok or not name:
                return

            contact, ok = QInputDialog.getText(
                self, "Add Supplier", "Enter Contact Number:"
            )
            if not ok or not contact:
                return

            address, ok = QInputDialog.getText(
                self, "Add Supplier", "Enter Address:"
            )
            if not ok or not address:
                return

            with Session(engine) as session:
                new_supplier = Supplier(
                    name=name,
                    contact_number=contact,
                    address=address,
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
        try:
            selected_row = self.supplier_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a supplier to update."
                )
                return

            supplier_id = int(self.supplier_table.item(selected_row, 0).text())

            name, ok = QInputDialog.getText(
                self, "Update Supplier", "Enter New Name:"
            )
            if not ok or not name:
                return

            contact, ok = QInputDialog.getText(
                self, "Update Supplier", "Enter New Contact Number:"
            )
            if not ok or not contact:
                return

            address, ok = QInputDialog.getText(
                self, "Update Supplier", "Enter New Address:"
            )
            if not ok or not address:
                return

            with Session(engine) as session:
                supplier = self.supplier_view.read_by_id(
                    db_session=session, record_id=supplier_id
                )
                if supplier:
                    supplier.name = name
                    supplier.contact_number = contact
                    supplier.address = address
                    self.supplier_view.update(
                        db_session=session,
                        record_id=supplier_id,
                        record=supplier,
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
        """Delete a supplier."""
        try:
            selected_row = self.supplier_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a supplier to delete."
                )
                return

            supplier_id = int(self.supplier_table.item(selected_row, 0).text())

            confirmation = QMessageBox.question(
                self,
                "Delete Supplier",
                "Are you sure you want to delete this supplier?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.supplier_view.delete(
                        db_session=session, record_id=supplier_id
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
