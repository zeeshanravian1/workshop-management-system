"""Inventory GUI Module.

Description:
- This module provides the GUI for managing inventory.

"""

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
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.supplier.gui import SupplierDialog
from workshop_management_system.v1.supplier.model import Supplier


class InventoryDialog(QDialog):
    """Dialog for adding/updating an inventory item."""

    def __init__(self, parent=None) -> None:
        """Initialize the Inventory Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Inventory Item Details")
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

        self.item_name_input = QLineEdit(self)
        self.quantity_input = QLineEdit(self)
        self.unit_price_input = QLineEdit(self)
        self.minimum_stock_level_input = QLineEdit(self)
        self.category_input = QLineEdit(self)
        self.reorder_level_input = QLineEdit(self)
        self.supplier_id_input = QComboBox(self)
        self.load_suppliers()

        self.form_layout.addRow("Item Name:", self.item_name_input)
        self.form_layout.addRow("Quantity:", self.quantity_input)
        self.form_layout.addRow("Unit Price:", self.unit_price_input)
        self.form_layout.addRow(
            "Minimum Stock Level:", self.minimum_stock_level_input
        )
        self.form_layout.addRow("Category:", self.category_input)
        self.form_layout.addRow("Reorder Level:", self.reorder_level_input)
        self.form_layout.addRow("Supplier:", self.supplier_id_input)

        self.buttons = QDialogButtonBox(
            (
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            ),
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def load_suppliers(self):
        """Load suppliers into the dropdown."""
        try:
            self.supplier_id_input.clear()
            self.supplier_id_input.addItem("Select Supplier", None)
            self.supplier_id_input.addItem("Add New Supplier", -1)
            with Session(engine) as session:
                suppliers = session.exec(select(Supplier)).all()
                for supplier in suppliers:
                    self.supplier_id_input.addItem(
                        f"{supplier.name} ({supplier.contact_number})",
                        supplier.id,
                    )
            self.supplier_id_input.currentIndexChanged.connect(
                self.check_add_new_supplier
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load suppliers: {e!s}"
            )

    def check_add_new_supplier(self, index):
        """Check if 'Add New Supplier' is selected and open SupplierDialog."""
        if self.supplier_id_input.currentData() == -1:
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
                        session.add(new_supplier)
                        session.commit()
                        self.supplier_id_input.blockSignals(True)
                        self.supplier_id_input.addItem(
                            f"{new_supplier.name} "
                            f"({new_supplier.contact_number})",
                            new_supplier.id,
                        )
                        self.supplier_id_input.setCurrentIndex(
                            self.supplier_id_input.count() - 1
                        )
                        self.supplier_id_input.blockSignals(False)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Failed to add supplier: {e!s}"
                    )
            else:
                self.supplier_id_input.blockSignals(True)
                self.supplier_id_input.setCurrentIndex(0)
                self.supplier_id_input.blockSignals(False)

    def get_data(self):
        """Get the data from the dialog."""
        return {
            "item_name": self.item_name_input.text(),
            "quantity": int(self.quantity_input.text()),
            "unit_price": float(self.unit_price_input.text()),
            "minimum_stock_level": int(self.minimum_stock_level_input.text()),
            "category": self.category_input.text(),
            "reorder_level": int(self.reorder_level_input.text()),
            "supplier_id": self.supplier_id_input.currentData(),
        }

    def accept(self):
        """Validate inputs before accepting the dialog."""
        try:
            float(self.unit_price_input.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Unit Price should be a float."
            )
            return

        try:
            int(self.quantity_input.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Quantity should be an integer."
            )
            return

        try:
            int(self.minimum_stock_level_input.text())
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Minimum Stock Level should be an integer.",
            )
            return

        try:
            int(self.reorder_level_input.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Reorder Level should be an integer."
            )
            return

        if self.supplier_id_input.currentData() is None:
            QMessageBox.warning(
                self, "Invalid Input", "Please select a supplier."
            )
            return

        super().accept()

    def set_data(self, data):
        """Set the data in the dialog fields."""
        self.item_name_input.setText(data["item_name"])
        self.quantity_input.setText(str(data["quantity"]))
        self.unit_price_input.setText(str(data["unit_price"]))
        self.minimum_stock_level_input.setText(
            str(data["minimum_stock_level"])
        )
        self.category_input.setText(data["category"])
        self.reorder_level_input.setText(str(data["reorder_level"]))
        self.supplier_id_input.setCurrentIndex(
            self.supplier_id_input.findData(data["supplier_id"])
        )


class InventoryGUI(QWidget):
    """Inventory GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Inventory GUI."""
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

        self.inventory_view = InventoryView(model=Inventory)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Inventory Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search inventory...")
        self.search_input.textChanged.connect(self.search_inventory)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(["Item Name", "Category", "Supplier"])
        self.search_criteria.currentTextChanged.connect(self.search_inventory)

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

        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setStyleSheet("""
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
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.horizontalHeader().setVisible(False)
        self.inventory_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.inventory_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_layout.addWidget(self.inventory_table)
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
            ("Load Inventory", self.load_inventory),
            ("Add Item", self.add_item),
            ("Update Item", self.update_item),
            ("Delete Item", self.delete_item),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_inventory()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_inventory(self) -> None:
        """Load inventory from the database and display them in the table."""
        try:
            with Session(engine) as session:
                inventory_items = self.inventory_view.read_all(
                    db_session=session
                )
                self.inventory_table.setRowCount(len(inventory_items) + 1)
                self.inventory_table.setColumnCount(7)
                self.inventory_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Item Name",
                        "Quantity",
                        "Unit Price",
                        "Minimum Stock Level",
                        "Category",
                        "Supplier ID",
                    ]
                )

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Item Name",
                    "Quantity",
                    "Unit Price",
                    "Minimum Stock Level",
                    "Category",
                    "Supplier ID",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.inventory_table.setItem(0, col, item)

                # Set the height of the first row
                self.inventory_table.setRowHeight(0, 40)

                for row, item in enumerate(inventory_items, start=1):
                    self.inventory_table.setItem(
                        row, 0, QTableWidgetItem(str(item.id))
                    )
                    self.inventory_table.setItem(
                        row, 1, QTableWidgetItem(item.item_name)
                    )
                    self.inventory_table.setItem(
                        row, 2, QTableWidgetItem(str(item.quantity))
                    )
                    self.inventory_table.setItem(
                        row, 3, QTableWidgetItem(str(item.unit_price))
                    )
                    self.inventory_table.setItem(
                        row, 4, QTableWidgetItem(str(item.minimum_stock_level))
                    )
                    self.inventory_table.setItem(
                        row, 5, QTableWidgetItem(item.category)
                    )
                    self.inventory_table.setItem(
                        row, 6, QTableWidgetItem(str(item.supplier_id))
                    )

                # Adjust column widths
                self.inventory_table.resizeColumnsToContents()
                self.inventory_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.inventory_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load inventory: {e!s}"
            )

    def add_item(self) -> None:
        """Add a new item to the inventory."""
        dialog = InventoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    supplier_query = select(Supplier).where(
                        Supplier.id == data["supplier_id"]
                    )
                    supplier = session.exec(supplier_query).first()
                    if not supplier:
                        raise ValueError("Supplier not found")

                    new_item = Inventory(
                        item_name=data["item_name"],
                        quantity=data["quantity"],
                        unit_price=data["unit_price"],
                        minimum_stock_level=data["minimum_stock_level"],
                        category=data["category"],
                        reorder_level=data["reorder_level"],
                        supplier_id=data["supplier_id"],
                    )
                    self.inventory_view.create(
                        db_session=session, record=new_item
                    )
                    QMessageBox.information(
                        self, "Success", "Item added successfully!"
                    )
                    self.load_inventory()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add item: {e!s}"
                )

    def update_item(self) -> None:
        """Update an existing item."""
        selected_row = self.inventory_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select an item to update."
            )
            return

        item = self.inventory_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected item ID is invalid."
            )
            return
        item_id = item.text()

        dialog = InventoryDialog(self)
        with Session(engine) as session:
            item_obj = self.inventory_view.read_by_id(
                db_session=session, record_id=int(item_id)
            )
            if item_obj:
                dialog.set_data(
                    {
                        "item_name": item_obj.item_name,
                        "quantity": item_obj.quantity,
                        "unit_price": item_obj.unit_price,
                        "minimum_stock_level": item_obj.minimum_stock_level,
                        "category": item_obj.category,
                        "reorder_level": item_obj.reorder_level,
                        "supplier_id": item_obj.supplier_id,
                    }
                )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    supplier = session.exec(
                        select(Supplier).where(
                            Supplier.id == data["supplier_id"]
                        )
                    ).first()
                    if not supplier:
                        raise ValueError("Supplier not found")

                    item_obj = self.inventory_view.read_by_id(
                        db_session=session, record_id=int(item_id)
                    )
                    if item_obj:
                        item_obj.item_name = data["item_name"]
                        item_obj.quantity = data["quantity"]
                        item_obj.unit_price = data["unit_price"]
                        item_obj.minimum_stock_level = data[
                            "minimum_stock_level"
                        ]
                        item_obj.category = data["category"]
                        item_obj.reorder_level = data["reorder_level"]
                        item_obj.supplier_id = data["supplier_id"]
                        self.inventory_view.update(
                            db_session=session,
                            record_id=int(item_id),
                            record=item_obj,
                        )
                        QMessageBox.information(
                            self, "Success", "Item updated successfully!"
                        )
                        self.load_inventory()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update item: {e!s}"
                )

    def delete_item(self) -> None:
        """Delete an item from the inventory."""
        try:
            selected_row = self.inventory_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an item to delete."
                )
                return

            item = self.inventory_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected item ID is invalid."
                )
                return
            item_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Item",
                "Are you sure you want to delete this item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.inventory_view.delete(
                        db_session=session, record_id=int(item_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Item deleted successfully!"
                    )
                    self.load_inventory()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete item: {e!s}"
            )

    def search_inventory(self) -> None:
        """Filter inventory based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.inventory_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "item name":
                    cell_text = self.inventory_table.item(row, 1)
                elif criteria == "category":
                    cell_text = self.inventory_table.item(row, 5)
                elif criteria == "supplier":
                    cell_text = self.inventory_table.item(row, 6)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.inventory_table.setRowHidden(row, not show_row)


if __name__ == "__main__":
    app = QApplication([])
    window = InventoryGUI()
    window.show()
    app.exec()
