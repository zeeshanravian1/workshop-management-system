"""Service Item GUI Module.

Description:
- This module provides the GUI for managing service items.
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
from workshop_management_system.v1.service_item.model import ServiceItem
from workshop_management_system.v1.service_item.view import ServiceItemView


class ServiceItemGUI(QMainWindow):
    """Service Item GUI Class.

    Description:
    - This class provides the GUI for managing service items.
    """

    def __init__(self) -> None:
        """Initialize the Service Item GUI."""
        super().__init__()
        self.setWindowTitle("Service Item Management")
        self.setGeometry(100, 100, 1000, 600)

        self.service_item_view = ServiceItemView(model=ServiceItem)

        self.main_layout = QVBoxLayout()

        # Service Item table
        self.service_item_table = QTableWidget()
        self.service_item_table.setSelectionBehavior(
            self.service_item_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.service_item_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Service Items")
        self.load_button.clicked.connect(self.load_service_items)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Service Item")
        self.add_button.clicked.connect(self.add_service_item)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Service Item")
        self.update_button.clicked.connect(self.update_service_item)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Service Item")
        self.delete_button.clicked.connect(self.delete_service_item)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_service_items()

    def load_service_items(self) -> None:
        """Load service items from the database and display them in the table."""
        try:
            with Session(engine) as session:
                items = self.service_item_view.read_all(db_session=session)
                self.service_item_table.setRowCount(len(items))
                self.service_item_table.setColumnCount(8)
                self.service_item_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Job Card ID",
                        "Item Name",
                        "Description",
                        "Quantity",
                        "Unit Price",
                        "Discount",
                        "Total Amount",
                    ]
                )

                for row, item in enumerate(items):
                    self.service_item_table.setItem(
                        row, 0, QTableWidgetItem(str(item.id))
                    )
                    self.service_item_table.setItem(
                        row, 1, QTableWidgetItem(str(item.job_card_id))
                    )
                    self.service_item_table.setItem(
                        row, 2, QTableWidgetItem(item.item_name)
                    )
                    self.service_item_table.setItem(
                        row, 3, QTableWidgetItem(str(item.item_description))
                    )
                    self.service_item_table.setItem(
                        row, 4, QTableWidgetItem(str(item.quantity))
                    )
                    self.service_item_table.setItem(
                        row, 5, QTableWidgetItem(str(item.unit_price))
                    )
                    self.service_item_table.setItem(
                        row, 6, QTableWidgetItem(str(item.discount))
                    )
                    self.service_item_table.setItem(
                        row, 7, QTableWidgetItem(str(item.total_amount))
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load service items: {e!s}"
            )

    def add_service_item(self) -> None:
        """Add a new service item to the database."""
        try:
            job_card_id, ok = QInputDialog.getInt(
                self,
                "Add Service Item",
                "Enter Job Card ID:",
                1,
                1,
                1000000,
                1,
            )
            if not ok:
                return

            item_name, ok = QInputDialog.getText(
                self, "Add Service Item", "Enter Item Name:"
            )
            if not ok or not item_name:
                return

            description, ok = QInputDialog.getText(
                self, "Add Service Item", "Enter Description:"
            )
            if not ok:  # Allow empty description
                return

            quantity, ok = QInputDialog.getInt(
                self, "Add Service Item", "Enter Quantity:", 1, 1, 1000, 1
            )
            if not ok:
                return

            unit_price, ok = QInputDialog.getDouble(
                self,
                "Add Service Item",
                "Enter Unit Price:",
                0.0,
                0.0,
                1000000.0,
                2,
            )
            if not ok:
                return

            discount, ok = QInputDialog.getDouble(
                self, "Add Service Item", "Enter Discount:", 0.0, 0.0, 100.0, 2
            )
            if not ok:
                return

            total_amount = quantity * unit_price * (1 - discount / 100)

            with Session(engine) as session:
                new_item = ServiceItem(
                    job_card_id=job_card_id,
                    item_name=item_name,
                    item_description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount,
                    total_amount=total_amount,
                )
                self.service_item_view.create(
                    db_session=session, record=new_item
                )
                QMessageBox.information(
                    self, "Success", "Service item added successfully!"
                )
                self.load_service_items()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add service item: {e!s}"
            )

    def update_service_item(self) -> None:
        """Update an existing service item."""
        try:
            selected_row = self.service_item_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service item to update."
                )
                return

            item_id = int(self.service_item_table.item(selected_row, 0).text())

            item_name, ok = QInputDialog.getText(
                self, "Update Service Item", "Enter New Item Name:"
            )
            if not ok or not item_name:
                return

            description, ok = QInputDialog.getText(
                self, "Update Service Item", "Enter New Description:"
            )
            if not ok:  # Allow empty description
                return

            quantity, ok = QInputDialog.getInt(
                self,
                "Update Service Item",
                "Enter New Quantity:",
                1,
                1,
                1000,
                1,
            )
            if not ok:
                return

            unit_price, ok = QInputDialog.getDouble(
                self,
                "Update Service Item",
                "Enter New Unit Price:",
                0.0,
                0.0,
                1000000.0,
                2,
            )
            if not ok:
                return

            discount, ok = QInputDialog.getDouble(
                self,
                "Update Service Item",
                "Enter New Discount:",
                0.0,
                0.0,
                100.0,
                2,
            )
            if not ok:
                return

            total_amount = quantity * unit_price * (1 - discount / 100)

            with Session(engine) as session:
                item_obj = self.service_item_view.read_by_id(
                    db_session=session, record_id=item_id
                )
                if item_obj:
                    item_obj.item_name = item_name
                    item_obj.item_description = description
                    item_obj.quantity = quantity
                    item_obj.unit_price = unit_price
                    item_obj.discount = discount
                    item_obj.total_amount = total_amount
                    self.service_item_view.update(
                        db_session=session,
                        record_id=item_id,
                        record=item_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Service item updated successfully!"
                    )
                    self.load_service_items()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update service item: {e!s}"
            )

    def delete_service_item(self) -> None:
        """Delete a service item from the database."""
        try:
            selected_row = self.service_item_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a service item to delete."
                )
                return

            item_id = int(self.service_item_table.item(selected_row, 0).text())

            confirmation = QMessageBox.question(
                self,
                "Delete Service Item",
                "Are you sure you want to delete this service item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.service_item_view.delete(
                        db_session=session, record_id=item_id
                    )
                    QMessageBox.information(
                        self, "Success", "Service item deleted successfully!"
                    )
                    self.load_service_items()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete service item: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = ServiceItemGUI()
    window.show()
    app.exec()
