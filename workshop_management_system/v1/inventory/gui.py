"""Inventory GUI Module.

Description:
- This module provides the GUI for managing inventory.

"""

from collections.abc import Sequence

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
from workshop_management_system.v1.inventory.association import (
    InventoryEstimate,
)
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.inventory.view import InventoryView
from workshop_management_system.v1.supplier.gui import SupplierDialog
from workshop_management_system.v1.supplier.model import Supplier
from workshop_management_system.v1.vehicle.model import Vehicle

from ..customer.model import Customer
from ..estimate.model import Estimate


class InventoryDialog(QDialog):
    """Dialog for adding/updating an inventory item."""

    def __init__(self, parent: QWidget | None = None) -> None:
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

    def load_suppliers(self) -> None:
        """Load suppliers into the dropdown."""
        try:
            self.supplier_id_input.clear()
            self.supplier_id_input.addItem("Select Supplier", None)
            self.supplier_id_input.addItem("Add New Supplier", -1)
            with Session(engine) as session:
                suppliers: Sequence[Supplier] = session.exec(
                    select(Supplier)
                ).all()
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

    def check_add_new_supplier(self, index: int) -> None:
        """Check if 'Add New Supplier' is selected and open SupplierDialog."""
        if self.supplier_id_input.currentData() == -1:
            dialog = SupplierDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data: dict[str, str] = dialog.get_data()
                try:
                    with Session(engine) as session:
                        new_supplier = Supplier(
                            name=data["name"],
                            email=data["email"],
                            contact_number=data["contact_number"],
                            address=data["address"],
                            id=None,  # Let the database generate the ID
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

    def get_data(self) -> dict[str, str]:
        """Get the data from the dialog."""
        return {
            "item_name": self.item_name_input.text(),
            "quantity": self.quantity_input.text(),
            "unit_price": self.unit_price_input.text(),
            "minimum_stock_level": self.minimum_stock_level_input.text(),
            "category": self.category_input.text(),
            "reorder_level": self.reorder_level_input.text(),
            "supplier_id": str(self.supplier_id_input.currentData()),
        }

    def accept(self) -> None:
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

    def set_data(self, data: dict[str, str | int | float]) -> None:
        """Set the data in the dialog fields."""
        self.item_name_input.setText(str(data["item_name"]))
        self.quantity_input.setText(str(data["quantity"]))
        self.unit_price_input.setText(str(data["unit_price"]))
        self.minimum_stock_level_input.setText(
            str(data["minimum_stock_level"])
        )
        self.category_input.setText(str(data["category"]))
        self.reorder_level_input.setText(str(data["reorder_level"]))
        self.supplier_id_input.setCurrentIndex(
            self.supplier_id_input.findData(data["supplier_id"])
        )


class ConsumptionDialog(QDialog):
    """Dialog for viewing inventory item consumptions."""

    def __init__(
        self, inventory_id: int, parent: QWidget | None = None
    ) -> None:
        """Initialize the Consumption Dialog."""
        super().__init__(parent)
        self.inventory_id = inventory_id
        self.setWindowTitle("Item Consumption History")
        self.setMinimumWidth(1000)  # Increased width
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Increased columns
        self.table.setHorizontalHeaderLabels(
            [
                "Estimate ID",
                "Date",
                "Customer Name",
                "Customer Contact",
                "Vehicle Info",
                "Quantity Used",
                "Unit Price",
                "Total Amount",
            ]
        )

        # Make table uneditable
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Set column stretching
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        # Set alternating row colors
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)

        layout.addWidget(self.table)

        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                font-size: 12px;
            }
        """)

        summary_layout = QFormLayout(summary_frame)
        self.total_quantity_label = QLabel()
        self.total_amount_label = QLabel()
        self.average_price_label = QLabel()

        # Add bold font to labels
        font = self.total_quantity_label.font()
        font.setBold(True)
        self.total_quantity_label.setFont(font)
        self.total_amount_label.setFont(font)
        self.average_price_label.setFont(font)

        summary_layout.addRow(
            "Total Quantity Used:", self.total_quantity_label
        )
        summary_layout.addRow("Total Amount:", self.total_amount_label)
        summary_layout.addRow("Average Unit Price:", self.average_price_label)
        layout.addWidget(summary_frame)

        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_consumptions()

    def load_consumptions(self) -> None:
        """Load consumption data from estimates."""
        try:
            with Session(engine) as session:
                # Restructure the join query to be explicit
                query = (
                    select(Estimate, Customer, InventoryEstimate, Vehicle)
                    .select_from(InventoryEstimate)
                    .join(
                        Estimate, InventoryEstimate.estimate_id == Estimate.id
                    )
                    .join(Customer, Estimate.customer_id == Customer.id)
                    .join(Vehicle, Estimate.vehicle_id == Vehicle.id)
                    .where(InventoryEstimate.inventory_id == self.inventory_id)
                    .order_by(Estimate.estimate_date.desc())
                )

                # Rest of the method remains the same
                result = session.exec(query)
                consumptions = list(result)

                # Populate table
                self.table.setRowCount(len(consumptions))
                total_quantity = 0
                total_amount = 0

                for row, (estimate, customer, inv_est, vehicle) in enumerate(
                    consumptions
                ):
                    # Format vehicle info
                    vehicle_info = f"{vehicle.make} {vehicle.model}"
                    f"({vehicle.engine_number})"

                    # Create and set table items
                    items = [
                        QTableWidgetItem(str(estimate.id)),
                        QTableWidgetItem(
                            estimate.estimate_date.strftime("%Y-%m-%d")
                        ),
                        QTableWidgetItem(customer.name),
                        QTableWidgetItem(customer.mobile_number),
                        QTableWidgetItem(vehicle_info),
                        QTableWidgetItem(str(inv_est.quantity_used)),
                        QTableWidgetItem(f"${inv_est.unit_price_at_time:.2f}"),
                        QTableWidgetItem(
                            f"${
                                inv_est.quantity_used *
                                inv_est.unit_price_at_time:.2f
                            }"
                        ),
                    ]

                    # Set items in row
                    for col, item in enumerate(items):
                        item.setFlags(
                            item.flags() & ~Qt.ItemFlag.ItemIsEditable
                        )  # Make item uneditable
                        self.table.setItem(row, col, item)

                    # Update totals
                    total_quantity += inv_est.quantity_used
                    amount = inv_est.quantity_used * inv_est.unit_price_at_time
                    total_amount += int(amount)

                # Adjust column widths
                self.table.resizeColumnsToContents()

                # Update summary with running totals
                self.total_quantity_label.setText(f"{total_quantity:,}")
                self.total_amount_label.setText(f"${total_amount:,.2f}")
                if total_quantity > 0:
                    avg_price = total_amount / total_quantity
                    self.average_price_label.setText(f"${avg_price:.2f}")
                else:
                    self.average_price_label.setText("N/A")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load consumption data: {e!s}"
            )


class InventoryGUI(QWidget):
    """Inventory GUI Class."""

    def __init__(self, parent: QWidget | None = None) -> None:
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
                border: 1px solid black;
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
        horizontal_header = QHeaderView(Qt.Orientation.Horizontal)
        vertical_header = QHeaderView(Qt.Orientation.Vertical)
        self.inventory_table.setHorizontalHeader(horizontal_header)
        self.inventory_table.setVerticalHeader(vertical_header)

        vertical_header.setVisible(False)
        horizontal_header.setVisible(False)
        self.inventory_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.inventory_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            ("View Consumptions", self.view_consumptions),  # Add new button
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

                for row, inventory_item in enumerate(inventory_items, start=1):
                    self.inventory_table.setItem(
                        row, 0, QTableWidgetItem(str(inventory_item.id))
                    )
                    self.inventory_table.setItem(
                        row, 1, QTableWidgetItem(inventory_item.item_name)
                    )
                    self.inventory_table.setItem(
                        row, 2, QTableWidgetItem(str(inventory_item.quantity))
                    )
                    self.inventory_table.setItem(
                        row,
                        3,
                        QTableWidgetItem(str(inventory_item.unit_price)),
                    )
                    self.inventory_table.setItem(
                        row,
                        4,
                        QTableWidgetItem(
                            str(inventory_item.minimum_stock_level)
                        ),
                    )
                    self.inventory_table.setItem(
                        row, 5, QTableWidgetItem(inventory_item.category)
                    )
                    self.inventory_table.setItem(
                        row,
                        6,
                        QTableWidgetItem(str(inventory_item.supplier_id)),
                    )

                # Adjust column widths
                self.inventory_table.resizeColumnsToContents()
                header = self.inventory_table.horizontalHeader()
                if header:
                    header.setStretchLastSection(True)
                    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
                        Supplier.id == int(data["supplier_id"])
                    )
                    supplier = session.exec(supplier_query).first()
                    if not supplier:
                        raise ValueError("Supplier not found")

                    new_item = Inventory(
                        id=None,  # Let the database generate the ID
                        item_name=data["item_name"],
                        quantity=int(data["quantity"]),
                        unit_price=int(data["unit_price"]),
                        minimum_stock_level=int(data["minimum_stock_level"]),
                        category=data["category"],
                        reorder_level=int(data["reorder_level"]),
                        supplier_id=int(data["supplier_id"]),
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
                            Supplier.id == int(data["supplier_id"])
                        )
                    ).first()
                    if not supplier:
                        raise ValueError("Supplier not found")

                    item_obj = self.inventory_view.read_by_id(
                        db_session=session, record_id=int(item_id)
                    )
                    if item_obj:
                        item_obj.item_name = data["item_name"]
                        item_obj.quantity = int(
                            float(data["quantity"])
                        )  # Convert to float first
                        item_obj.unit_price = float(
                            data["unit_price"]
                        )  # Keep as float
                        item_obj.minimum_stock_level = int(
                            float(data["minimum_stock_level"])
                        )
                        item_obj.category = data["category"]
                        item_obj.reorder_level = int(
                            float(data["reorder_level"])
                        )
                        item_obj.supplier_id = int(data["supplier_id"])
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
                    cell_text = str(self.inventory_table.item(row, 1))
                elif criteria == "category":
                    cell_text = str(self.inventory_table.item(row, 5))
                elif criteria == "supplier":
                    cell_text = str(self.inventory_table.item(row, 6))

                if (
                    isinstance(cell_text, QTableWidgetItem)
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.inventory_table.setRowHidden(row, not show_row)

    def view_consumptions(self) -> None:
        """View consumption history for selected inventory item."""
        selected_row = self.inventory_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select an item to view consumptions."
            )
            return

        item = self.inventory_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected item ID is invalid."
            )
            return

        dialog = ConsumptionDialog(int(item.text()), self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication([])
    window = InventoryGUI()
    window.show()
    app.exec()
