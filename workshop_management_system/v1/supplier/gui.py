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
    """Supplier GUI Class.

    Description:
    - This class provides the GUI for managing suppliers.

    """

    def __init__(self) -> None:
        """Initialize the Supplier GUI."""
        super().__init__()
        self.setWindowTitle("Supplier Management")
        self.setGeometry(100, 100, 800, 600)

        self.supplier_view = SupplierView(
            model=Supplier
        )  # Initialize SupplierView for CRUD operations

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

        self.load_suppliers()  # Load suppliers on initialization

    def load_suppliers(self) -> None:
        """Load suppliers from the database and display them in the table."""
        try:
            with Session(engine) as session:
                suppliers = self.supplier_view.read_all(db_session=session)
                self.supplier_table.setRowCount(len(suppliers))
                self.supplier_table.setColumnCount(2)
                self.supplier_table.setHorizontalHeaderLabels(
                    ["ID", "Name"]
                )

                for row, supplier in enumerate(suppliers):
                    self.supplier_table.setItem(
                        row, 0, QTableWidgetItem(str(supplier.supplier_id))
                    )
                    self.supplier_table.setItem(
                        row, 1, QTableWidgetItem(supplier.name)
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load suppliers: {e!s}"
            )

    def add_supplier(self) -> None:
        """Add a new supplier to the database."""
        try:
            # Get supplier details from user
            name, ok = QInputDialog.getText(
                self, "Add Supplier", "Enter Supplier Name:"
            )
            if not ok or not name:
                return

            with Session(engine) as session:
                new_supplier = Supplier(name=name)
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

            item = self.supplier_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected supplier ID is invalid."
                )
                return
            supplier_id = item.text()

            # Get updated details from user
            name, ok = QInputDialog.getText(
                self, "Update Supplier", "Enter New Name:"
            )
            if not ok or not name:
                return

            with Session(engine) as session:
                supplier_obj = self.supplier_view.read_by_id(
                    db_session=session, record_id=int(supplier_id)
                )
                if supplier_obj:
                    supplier_obj.name = name
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
