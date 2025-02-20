"""Estimate GUI Module.

Description:
- This module provides the GUI for managing estimates.

"""

import webbrowser
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
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
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.estimate.model import Estimate
from workshop_management_system.v1.estimate.view import EstimateView
from workshop_management_system.v1.inventory.association import (
    InventoryEstimate,  # Add this import
)
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.vehicle.model import Vehicle


class InventoryItemsDialog(QDialog):
    """Dialog for selecting inventory items."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Inventory Items")
        self.setMinimumWidth(600)
        self.selected_items = []

        # Initialize tracking dictionaries first
        self.selected_checkboxes = {}
        self.current_quantities = {}

        layout = QVBoxLayout(self)

        # Create inventory items table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "Select",
                "Item Name",
                "Available Quantity",
                "Unit Price",
                "Quantity to Use",
            ]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Add a status label for showing quantity info
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 10px;
                background-color: #f8f8f8;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-size: 12px;
                min-height: 100px;
            }
        """)
        layout.addWidget(self.status_label)

        # Add quantity validation
        self.current_quantities = {}  # Track quantities for each item

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.load_inventory_items()

    def load_inventory_items(self) -> None:
        """Load inventory items into the table."""
        try:
            with Session(engine) as session:
                items = session.exec(select(Inventory)).all()
                self.table.setRowCount(len(items))

                for row, item in enumerate(items):
                    # Checkbox with state change tracking
                    checkbox = QTableWidgetItem()
                    checkbox.setFlags(
                        Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsEnabled
                    )
                    checkbox.setCheckState(Qt.CheckState.Unchecked)
                    self.table.setItem(row, 0, checkbox)

                    # Store item name for checkbox tracking
                    self.selected_checkboxes[row] = item.item_name

                    # Item details
                    self.table.setItem(
                        row, 1, QTableWidgetItem(item.item_name)
                    )
                    self.table.setItem(
                        row, 2, QTableWidgetItem(str(item.quantity))
                    )
                    self.table.setItem(
                        row, 3, QTableWidgetItem(f"${item.unit_price:.2f}")
                    )

                    # Quantity input with combined validation
                    quantity_input = QLineEdit()
                    quantity_input.setValidator(
                        QIntValidator(0, item.quantity)
                    )
                    quantity_input.textChanged.connect(
                        lambda text,
                        r=row,
                        max_qty=item.quantity,
                        name=item.item_name: self.update_selection(
                            r, text, max_qty, name
                        )
                    )
                    self.table.setCellWidget(row, 4, quantity_input)

                # Connect checkbox state change
                self.table.itemChanged.connect(self.on_checkbox_changed)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load inventory items: {e}"
            )

    def on_checkbox_changed(self, item):
        """Handle checkbox state changes."""
        if item.column() == 0:  # Checkbox column
            row = item.row()
            item_name = self.selected_checkboxes.get(row)
            if item_name:
                if item.checkState() == Qt.CheckState.Checked:
                    # Initialize quantity if checked
                    quantity_widget = self.table.cellWidget(row, 4)
                    if quantity_widget and quantity_widget.text():
                        self.current_quantities[item_name] = int(
                            quantity_widget.text()
                        )
                    else:
                        self.current_quantities[item_name] = 0
                else:
                    # Remove quantity if unchecked
                    self.current_quantities.pop(item_name, None)
                self.update_status_label()

    def update_selection(
        self, row: int, text: str, max_qty: int, item_name: str
    ) -> None:
        """Update both quantity and selection status."""
        try:
            checkbox = self.table.item(row, 0)
            if not checkbox:
                return

            if text and int(text) > 0:
                # Auto-check checkbox if quantity is entered
                checkbox.setCheckState(Qt.CheckState.Checked)
                qty = min(int(text), max_qty)
                self.current_quantities[item_name] = qty
            else:
                # Auto-uncheck if quantity is 0 or empty
                checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.current_quantities.pop(item_name, None)

            self.update_status_label()

        except ValueError:
            self.current_quantities.pop(item_name, None)
            self.update_status_label()

    def update_status_label(self):
        """Update status label with all selected items."""
        status_text = "Selected Items:\n\n"
        total_items = 0
        total_amount = 0

        for row in range(self.table.rowCount()):
            checkbox = self.table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                item_name = self.table.item(row, 1).text()
                quantity = self.current_quantities.get(item_name, 0)
                if quantity > 0:
                    unit_price = float(
                        self.table.item(row, 3).text().replace("$", "")
                    )
                    item_total = quantity * unit_price
                    status_text += f"• {item_name}: {quantity} units (${item_total:.2f})\n"
                    total_items += quantity
                    total_amount += item_total

        status_text += f"\nTotal Items: {total_items}"
        status_text += f"\nTotal Amount: ${total_amount:.2f}"
        self.status_label.setText(status_text)

    def get_selected_items(self):
        """Get the selected inventory items and their quantities."""
        selected = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                quantity_widget = self.table.cellWidget(row, 4)
                if quantity_widget and quantity_widget.text():
                    quantity = int(quantity_widget.text())
                    if quantity > 0:  # Only include items with quantity > 0
                        selected.append(
                            {
                                "item_name": self.table.item(row, 1).text(),
                                "quantity": quantity,
                                "unit_price": float(
                                    self.table.item(row, 3)
                                    .text()
                                    .replace("$", "")
                                ),
                            }
                        )
        return selected


class EstimateDialog(QDialog):
    """Dialog for adding/updating an estimate."""

    def __init__(self, parent=None, estimate_data=None) -> None:
        """Initialize the Estimate Dialog.

        Args:
            parent: Parent widget
            estimate_data: Dictionary containing estimate data for update mode
        """
        super().__init__(parent)
        self.setWindowTitle("Estimate Details")
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

        self.total_amount_input = QLineEdit(self)
        # Replace the QLineEdit with QComboBox for status
        self.status_input = QComboBox(self)
        self.status_input.addItems(
            ["Pending", "In Progress", "Completed", "Cancelled"]
        )
        self.description_input = QLineEdit(self)
        self.valid_until_input = QLineEdit(self)
        self.vehicle_id_input = QLineEdit(self)
        self.job_card_id_input = QLineEdit(self)
        self.customer_id_input = QLineEdit(self)

        self.form_layout.addRow(
            "Total Estimate Amount:", self.total_amount_input
        )
        self.form_layout.addRow("Status:", self.status_input)
        self.form_layout.addRow(
            "Description (optional):", self.description_input
        )
        self.form_layout.addRow(
            "Valid Until (YYYY-MM-DD):", self.valid_until_input
        )
        self.form_layout.addRow("Vehicle ID:", self.vehicle_id_input)
        self.form_layout.addRow(
            "Job Card ID (optional):", self.job_card_id_input
        )
        self.form_layout.addRow("Customer ID:", self.customer_id_input)

        # Add inventory items section
        self.inventory_items_table = QTableWidget()
        self.inventory_items_table.setColumnCount(3)
        self.inventory_items_table.setHorizontalHeaderLabels(
            ["Item Name", "Quantity", "Unit Price"]
        )
        self.form_layout.addRow(self.inventory_items_table)

        # Add button to select inventory items
        select_items_button = QPushButton("Select Inventory Items")
        select_items_button.clicked.connect(self.select_inventory_items)
        self.form_layout.addRow(select_items_button)

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

        self.original_quantities = {}  # Store original quantities for updates
        self.selected_items = []

        # Add a flag to track if this is an update operation
        self.is_update = estimate_data is not None
        self.estimate_id = None  # Store estimate ID for updates

        # Pre-populate fields if estimate_data is provided
        if estimate_data:
            self.total_amount_input.setText(str(estimate_data["total_amount"]))
            # Set the current status in the combo box
            self.status_input.setCurrentText(estimate_data["status"])
            self.description_input.setText(estimate_data["description"] or "")
            self.valid_until_input.setText(estimate_data["valid_until"])
            self.vehicle_id_input.setText(str(estimate_data["vehicle_id"]))
            self.job_card_id_input.setText(
                str(estimate_data["job_card_id"])
                if estimate_data["job_card_id"]
                else ""
            )
            self.customer_id_input.setText(str(estimate_data["customer_id"]))

            # Pre-populate inventory items
            self.selected_items = estimate_data.get("inventory_items", [])
            self.update_inventory_items_table()
            self.estimate_id = estimate_data.get("id")  # Store the estimate ID
            # Load existing inventory items into original quantities
            for item in self.selected_items:
                self.original_quantities[item["item_name"]] = item["quantity"]

    def select_inventory_items(self):
        """Open dialog to select inventory items."""
        dialog = InventoryItemsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_items = dialog.get_selected_items()

            # Store the difference in quantities for existing items
            for item in new_items:
                item_name = item["item_name"]
                if item_name not in self.original_quantities:
                    self.original_quantities[item_name] = item["quantity"]

            self.selected_items = new_items
            self.update_inventory_items_table()

    def get_quantity_changes(self):
        """Get the changes in quantities for inventory items."""
        changes = {}
        for item in self.selected_items:
            item_name = item["item_name"]
            original = self.original_quantities.get(item_name, 0)
            current = item["quantity"]
            if original != current:
                changes[item_name] = current - original
        return changes

    def update_inventory_items_table(self):
        """Update the inventory items table with selected items."""
        self.inventory_items_table.setRowCount(len(self.selected_items))

        for row, item in enumerate(self.selected_items):
            self.inventory_items_table.setItem(
                row, 0, QTableWidgetItem(item["item_name"])
            )
            self.inventory_items_table.setItem(
                row, 1, QTableWidgetItem(str(item["quantity"]))
            )
            self.inventory_items_table.setItem(
                row, 2, QTableWidgetItem(f"${item['unit_price']:.2f}")
            )

    def get_data(self):
        """Get the data from the dialog."""
        if not self.total_amount_input.text().strip():
            QMessageBox.warning(
                self, "Validation Error", "Total amount cannot be empty!"
            )
            return None

        try:
            total_amount = float(self.total_amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Total amount must be a valid number!",
            )
            return None

        return {
            "total_amount": total_amount,
            "status": self.status_input.currentText(),
            "description": self.description_input.text(),
            "valid_until": self.valid_until_input.text(),
            "vehicle_id": self.vehicle_id_input.text(),
            "job_card_id": self.job_card_id_input.text(),
            "customer_id": self.customer_id_input.text(),
            "inventory_items": self.selected_items,
        }


class EstimateGUI(QWidget):
    """Estimate GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Estimate GUI."""
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

        self.estimate_view = EstimateView(model=Estimate)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Estimate Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search estimates...")
        self.search_input.textChanged.connect(self.search_estimates)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Customer ID", "Vehicle ID", "Status", "Description"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_estimates)

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

        # Estimate table
        self.estimate_table = QTableWidget()
        self.estimate_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.estimate_table.setAlternatingRowColors(True)
        self.estimate_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.estimate_table.setStyleSheet("""
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
        self.estimate_table.verticalHeader().setVisible(False)
        self.estimate_table.horizontalHeader().setVisible(False)
        self.estimate_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.estimate_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.estimate_table.horizontalHeader().setStretchLastSection(True)
        self.estimate_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_layout.addWidget(self.estimate_table)
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
            ("Load Estimates", self.load_estimates),
            ("Add Estimate", self.add_estimate),
            ("Update Estimate", self.update_estimate),
            ("Delete Estimate", self.delete_estimate),
            ("Generate PDF", self.generate_pdf),  # Add the PDF button
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        self.load_estimates()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_estimates(self) -> None:
        """Load estimates from the database and display them in the table."""
        try:
            with Session(engine) as session:
                estimates = self.estimate_view.read_all(db_session=session)
                self.estimate_table.setRowCount(len(estimates) + 1)
                self.estimate_table.setColumnCount(9)
                self.estimate_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Estimate Date",
                        "Total Amount",
                        "Status",
                        "Description",
                        "Valid Until",
                        "Customer ID",
                        "Vehicle ID",
                        "Job Card ID",
                    ]
                )

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Estimate Date",
                    "Total Amount",
                    "Status",
                    "Description",
                    "Valid Until",
                    "Customer ID",
                    "Vehicle ID",
                    "Job Card ID",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.estimate_table.setItem(0, col, item)

                # Set the height of the first row
                self.estimate_table.setRowHeight(0, 40)

                for row, estimate in enumerate(estimates, start=1):
                    self.estimate_table.setItem(
                        row, 0, QTableWidgetItem(str(estimate.id))
                    )
                    self.estimate_table.setItem(
                        row, 1, QTableWidgetItem(str(estimate.estimate_date))
                    )
                    self.estimate_table.setItem(
                        row,
                        2,
                        QTableWidgetItem(str(estimate.total_estimate_amount)),
                    )
                    self.estimate_table.setItem(
                        row, 3, QTableWidgetItem(estimate.status)
                    )
                    self.estimate_table.setItem(
                        row, 4, QTableWidgetItem(estimate.description or "")
                    )
                    self.estimate_table.setItem(
                        row, 5, QTableWidgetItem(str(estimate.valid_until))
                    )
                    self.estimate_table.setItem(
                        row, 6, QTableWidgetItem(str(estimate.customer_id))
                    )
                    self.estimate_table.setItem(
                        row, 7, QTableWidgetItem(str(estimate.vehicle_id))
                    )
                    self.estimate_table.setItem(
                        row,
                        8,
                        QTableWidgetItem(
                            str(estimate.job_card_id)
                            if estimate.job_card_id
                            else ""
                        ),
                    )

                # Adjust column widths
                self.estimate_table.resizeColumnsToContents()
                self.estimate_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.estimate_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load estimates: {e!s}"
            )

    def add_estimate(self) -> None:
        """Add a new estimate to the database."""
        dialog = EstimateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is not None:  # Only proceed if data is valid
                try:
                    with Session(engine) as session:
                        vehicle = session.exec(
                            select(Vehicle).where(
                                Vehicle.id == int(data["vehicle_id"])
                            )
                        ).first()
                        if not vehicle:
                            raise ValueError("Vehicle not found")

                        new_estimate = Estimate(
                            estimate_date=datetime.now(),
                            total_estimate_amount=data["total_amount"],
                            status=data["status"],
                            description=data["description"],
                            valid_until=datetime.strptime(
                                data["valid_until"], "%Y-%m-%d"
                            ),
                            customer_id=vehicle.customer_id,
                            vehicle_id=vehicle.id,
                            job_card_id=int(data["job_card_id"])
                            if data["job_card_id"]
                            else None,
                        )
                        session.add(new_estimate)
                        session.flush()  # Get the new estimate ID

                        # Add inventory items with quantity tracking
                        total_amount = 0
                        for item in data["inventory_items"]:
                            inventory = session.exec(
                                select(Inventory).where(
                                    Inventory.item_name == item["item_name"]
                                )
                            ).first()

                            if inventory:
                                # Update inventory quantity
                                inventory.quantity -= item["quantity"]

                                # Create association
                                association = InventoryEstimate(
                                    inventory_id=inventory.id,
                                    estimate_id=new_estimate.id,
                                    quantity_used=item["quantity"],
                                    unit_price_at_time=item["unit_price"],
                                )
                                session.add(association)

                                # Update total amount
                                total_amount += (
                                    item["quantity"] * item["unit_price"]
                                )

                        # Update estimate total amount
                        new_estimate.total_estimate_amount = total_amount
                        session.commit()
                        QMessageBox.information(
                            self, "Success", "Estimate added successfully!"
                        )
                        self.load_estimates()
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Failed to add estimate: {e!s}"
                    )

    def update_estimate(self) -> None:
        """Update an existing estimate."""
        selected_row = self.estimate_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select an estimate to update."
            )
            return

        item = self.estimate_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected estimate ID is invalid."
            )
            return
        estimate_id = item.text()

        try:
            with Session(engine) as session:
                # Get the existing estimate data
                estimate = self.estimate_view.read_by_id(
                    db_session=session, record_id=int(estimate_id)
                )

                if not estimate:
                    raise ValueError("Estimate not found")

                # Get related inventory items with a proper join
                inventory_items = (
                    session.query(InventoryEstimate, Inventory)
                    .join(
                        Inventory,
                        InventoryEstimate.inventory_id == Inventory.id,
                    )
                    .filter(InventoryEstimate.estimate_id == int(estimate_id))
                    .all()
                )

                # Prepare data for the dialog
                estimate_data = {
                    "id": estimate_id,  # Add estimate ID to the data
                    "total_amount": estimate.total_estimate_amount,
                    "status": estimate.status,
                    "description": estimate.description,
                    "valid_until": estimate.valid_until.strftime("%Y-%m-%d"),
                    "vehicle_id": estimate.vehicle_id,
                    "job_card_id": estimate.job_card_id,
                    "customer_id": estimate.customer_id,
                    "inventory_items": [
                        {
                            "item_name": inventory.item_name,
                            "quantity": inv_estimate.quantity_used,
                            "unit_price": inv_estimate.unit_price_at_time,
                        }
                        for inv_estimate, inventory in inventory_items
                    ],
                }

                # Create dialog with pre-populated data
                dialog = EstimateDialog(self, estimate_data)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    try:
                        with Session(engine) as session:
                            # First, delete existing inventory associations
                            session.query(InventoryEstimate).filter(
                                InventoryEstimate.estimate_id
                                == int(estimate_id)
                            ).delete()

                            # Update the estimate and create new inventory associations
                            vehicle = session.exec(
                                select(Vehicle).where(
                                    Vehicle.id == int(data["vehicle_id"])
                                )
                            ).first()
                            if not vehicle:
                                raise ValueError("Vehicle not found")

                            estimate_obj = self.estimate_view.read_by_id(
                                db_session=session, record_id=int(estimate_id)
                            )
                            if estimate_obj:
                                # Update inventory quantities for new selections
                                total_amount = 0
                                for item in data["inventory_items"]:
                                    inventory = session.exec(
                                        select(Inventory).where(
                                            Inventory.item_name
                                            == item["item_name"]
                                        )
                                    ).first()

                                    if inventory:
                                        # Create new association
                                        association = InventoryEstimate(
                                            inventory_id=inventory.id,
                                            estimate_id=estimate_obj.id,
                                            quantity_used=item["quantity"],
                                            unit_price_at_time=item[
                                                "unit_price"
                                            ],
                                        )
                                        session.add(association)

                                        # Update inventory quantity
                                        original_qty = (
                                            dialog.original_quantities.get(
                                                item["item_name"], 0
                                            )
                                        )
                                        qty_change = (
                                            item["quantity"] - original_qty
                                        )
                                        inventory.quantity -= qty_change

                                        total_amount += (
                                            item["quantity"]
                                            * item["unit_price"]
                                        )

                                # Update estimate
                                estimate_obj.total_estimate_amount = (
                                    total_amount
                                )
                                estimate_obj.estimate_date = datetime.now()
                                estimate_obj.status = data["status"]
                                estimate_obj.description = data["description"]
                                estimate_obj.valid_until = datetime.strptime(
                                    data["valid_until"], "%Y-%m-%d"
                                )
                                estimate_obj.customer_id = vehicle.customer_id
                                estimate_obj.vehicle_id = vehicle.id
                                estimate_obj.job_card_id = (
                                    int(data["job_card_id"])
                                    if data["job_card_id"]
                                    else None
                                )

                                session.commit()
                                QMessageBox.information(
                                    self,
                                    "Success",
                                    "Estimate updated successfully!",
                                )
                                self.load_estimates()

                    except Exception as e:
                        session.rollback()
                        QMessageBox.critical(
                            self, "Error", f"Failed to update estimate: {e!s}"
                        )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update estimate: {e!s}"
            )

    def delete_estimate(self) -> None:
        """Delete an estimate from the database."""
        try:
            selected_row = self.estimate_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select an estimate to delete."
                )
                return

            item = self.estimate_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected estimate ID is invalid."
                )
                return
            estimate_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Estimate",
                "Are you sure you want to delete this estimate?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.estimate_view.delete(
                        db_session=session, record_id=int(estimate_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Estimate deleted successfully!"
                    )
                    self.load_estimates()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete estimate: {e!s}"
            )

    def search_estimates(self) -> None:
        """Filter estimates based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.estimate_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "customer id":
                    cell_text = self.estimate_table.item(row, 1)
                elif criteria == "vehicle id":
                    cell_text = self.estimate_table.item(row, 2)
                elif criteria == "status":
                    cell_text = self.estimate_table.item(row, 3)
                elif criteria == "description":
                    cell_text = self.estimate_table.item(row, 4)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.estimate_table.setRowHidden(row, not show_row)

    def generate_pdf(self) -> None:
        """Generate PDF for the selected estimate."""
        selected_row = self.estimate_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select an estimate to generate PDF."
            )
            return

        item = self.estimate_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected estimate ID is invalid."
            )
            return

        estimate_id = int(item.text())

        try:
            with Session(engine) as session:
                # Get estimate with related inventory items
                estimate = self.estimate_view.read_by_id(
                    db_session=session, record_id=estimate_id
                )

                if not estimate:
                    raise ValueError("Estimate not found")

                # Get inventory items with joined Inventory table
                stmt = (
                    select(InventoryEstimate, Inventory)
                    .join(
                        Inventory,
                        InventoryEstimate.inventory_id == Inventory.id,
                    )
                    .where(InventoryEstimate.estimate_id == estimate_id)
                )
                inventory_items = session.exec(stmt).all()

                # Generate PDF
                filename = f"estimate_{estimate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                self.generate_estimate_pdf(estimate, inventory_items, filename)

                # Open the generated PDF
                webbrowser.open_new_tab(filename)

                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF generated successfully!\nSaved as: {filename}",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to generate PDF: {e!s}"
            )

    def generate_estimate_pdf(self, estimate, inventory_items, filename):
        """Generate detailed PDF for an estimate."""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        elements.append(Paragraph(f"Estimate #{estimate.id}", styles["Title"]))
        elements.append(
            Paragraph(
                f"Date: {estimate.estimate_date.strftime('%Y-%m-%d')}",
                styles["Normal"],
            )
        )
        elements.append(Paragraph("<br/><br/>", styles["Normal"]))

        # Basic Estimate Details
        estimate_data = [
            ["Vehicle ID:", str(estimate.vehicle_id)],
            ["Status:", estimate.status],
            ["Description:", estimate.description or "N/A"],
            ["Valid Until:", estimate.valid_until.strftime("%Y-%m-%d")],
        ]

        basic_table = Table(estimate_data, colWidths=[100, 400])
        basic_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(basic_table)
        elements.append(Paragraph("<br/><br/>", styles["Normal"]))

        # Inventory Items Table
        if inventory_items:
            elements.append(Paragraph("Inventory Items", styles["Heading2"]))
            items_data = [["Item", "Quantity", "Unit Price", "Total"]]
            subtotal = 0

            for (
                inv_estimate,
                inventory,
            ) in inventory_items:  # Modified this line
                item_total = (
                    inv_estimate.quantity_used
                    * inv_estimate.unit_price_at_time
                )
                subtotal += item_total
                items_data.append(
                    [
                        str(inventory.item_name),  # Use inventory directly
                        str(inv_estimate.quantity_used),
                        f"${inv_estimate.unit_price_at_time:.2f}",
                        f"${item_total:.2f}",
                    ]
                )

            # Calculate GST and total
            gst = subtotal * 0.18  # 18% GST
            grand_total = subtotal + gst

            # Add totals to the table
            items_data.extend(
                [
                    ["", "", "Subtotal:", f"${subtotal:.2f}"],
                    ["", "", "GST (18%):", f"${gst:.2f}"],
                    ["", "", "Grand Total:", f"${grand_total:.2f}"],
                ]
            )

            items_table = Table(items_data, colWidths=[200, 100, 100, 100])
            items_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        (
                            "ALIGN",
                            (-1, 0),
                            (-1, -1),
                            "RIGHT",
                        ),  # Right align amounts
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        (
                            "BACKGROUND",
                            (0, -3),
                            (-1, -1),
                            colors.lightgrey,
                        ),  # Highlight totals
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            elements.append(items_table)
        else:
            elements.append(
                Paragraph("No inventory items found.", styles["Normal"])
            )

        # Footer
        elements.append(Paragraph("<br/><br/>", styles["Normal"]))
        elements.append(Paragraph("Terms and Conditions:", styles["Heading2"]))
        elements.append(
            Paragraph("1. All prices are in USD", styles["Normal"])
        )
        elements.append(
            Paragraph("2. Estimate valid for 30 days", styles["Normal"])
        )
        elements.append(
            Paragraph(
                "3. Final price may vary based on additional services",
                styles["Normal"],
            )
        )

        doc.build(elements)


if __name__ == "__main__":
    app = QApplication([])
    window = EstimateGUI()
    window.show()
    app.exec()
