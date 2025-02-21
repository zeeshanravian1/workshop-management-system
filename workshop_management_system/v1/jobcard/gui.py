"""JobCard GUI Module.

Description:
- This module provides the GUI for managing job cards.

"""

import webbrowser
from datetime import datetime

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QCalendarWidget,
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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.inventory.association import (
    InventoryEstimate,
)
from workshop_management_system.v1.inventory.model import Inventory
from workshop_management_system.v1.jobcard.model import JobCard
from workshop_management_system.v1.jobcard.view import JobCardView
from workshop_management_system.v1.vehicle.model import Vehicle

from ..utils.pdf_generator import generate_jobcard_pdf


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
                    # Checkbox
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

                    # Quantity input
                    quantity_input = QLineEdit()
                    quantity_input.setValidator(QIntValidator(0, 999999))
                    quantity_input.textChanged.connect(
                        lambda text,
                        r=row,
                        name=item.item_name: self.update_selection(
                            r, text, name
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

    def update_selection(self, row: int, text: str, item_name: str) -> None:
        """Update both quantity and selection status."""
        try:
            checkbox = self.table.item(row, 0)
            if not checkbox:
                return

            if text and int(text) > 0:
                # Auto-check checkbox if quantity is entered
                checkbox.setCheckState(Qt.CheckState.Checked)
                self.current_quantities[item_name] = int(text)
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


class JobCardDialog(QDialog):
    """Dialog for adding/updating a job card."""

    def __init__(self, parent=None, jobcard=None) -> None:
        """Initialize the JobCard Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Job Card Details")
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

        # Add status input
        self.status_input = QComboBox(self)
        self.status_input.addItems(["Pending", "Completed", "Cancelled"])

        self.vehicle_id_input = QComboBox(self)
        self.load_vehicles()

        # Create the calendar widget but keep it hidden initially
        self.calendar = QCalendarWidget(self)
        self.calendar.setWindowFlags(Qt.WindowType.Popup)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.hide()

        # Create date layout for service date
        date_layout = QHBoxLayout()
        self.service_date_input = QLineEdit(self)
        self.service_date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        date_layout.addWidget(self.service_date_input)

        # Calendar button
        self.calendar_button = QPushButton("📅")
        self.calendar_button.setMaximumWidth(40)
        self.calendar_button.clicked.connect(self.show_calendar)
        date_layout.addWidget(self.calendar_button)

        # Replace the old form layout line with the new date layout
        self.form_layout.addRow("Service Date (YYYY-MM-DD):", date_layout)

        self.description_input = QLineEdit(self)

        self.form_layout.addRow("Vehicle ID:", self.vehicle_id_input)
        self.form_layout.addRow(
            "Status:", self.status_input
        )  # Add status field to form
        self.form_layout.addRow("Description:", self.description_input)

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

        self.selected_items = []

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

        # If jobcard data is provided, populate the fields
        if jobcard:
            # Find and select the correct vehicle in combobox
            index = self.vehicle_id_input.findData(jobcard.vehicle_id)
            if index >= 0:
                self.vehicle_id_input.setCurrentIndex(index)

            self.service_date_input.setText(str(jobcard.service_date))
            self.description_input.setText(jobcard.description)
            self.status_input.setCurrentText(jobcard.status)

    def show_calendar(self):
        """Show calendar widget below the date input."""
        try:
            # Try to set the calendar to the current input date
            current_date = datetime.strptime(
                self.service_date_input.text(), "%Y-%m-%d"
            ).date()
            self.calendar.setSelectedDate(
                QDate(current_date.year, current_date.month, current_date.day)
            )
        except ValueError:
            # If current date is invalid, use today's date
            today = datetime.today()
            self.calendar.setSelectedDate(
                QDate(today.year, today.month, today.day)
            )

        # Position the calendar below the input field
        pos = self.service_date_input.mapToGlobal(
            self.service_date_input.rect().bottomLeft()
        )
        self.calendar.move(pos)
        self.calendar.show()

    def on_date_selected(self):
        """Handle date selection from calendar."""
        selected_date = self.calendar.selectedDate()
        formatted_date = f"{selected_date.year()}-{selected_date.month():02d}-{selected_date.day():02d}"
        self.service_date_input.setText(formatted_date)
        self.calendar.hide()

    def load_vehicles(self):
        """Load vehicles from the database and populate the dropdown."""
        try:
            with Session(engine) as session:
                vehicles = session.query(Vehicle).all()
                for vehicle in vehicles:
                    self.vehicle_id_input.addItem(
                        f"{vehicle.id} - {vehicle.vehicle_number}", vehicle.id
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load vehicles: {e!s}"
            )

    def get_data(self) -> dict:
        """Get the data from the dialog fields."""
        try:
            # Get and validate vehicle_id
            vehicle_id = self.vehicle_id_input.currentData()
            if not vehicle_id:
                raise ValueError("Vehicle ID cannot be empty")

            # Get and validate status
            status = self.status_input.currentText()
            if not status:
                raise ValueError("Status cannot be empty")

            # Get and validate service date
            service_date = self.service_date_input.text().strip()
            if not service_date:
                raise ValueError("Service date cannot be empty")
            try:
                datetime.strptime(service_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")

            # Get and validate description
            description = self.description_input.text().strip()
            if not description:
                raise ValueError("Description cannot be empty")
            if len(description) < 5:
                raise ValueError(
                    "Description must be at least 5 characters long"
                )

            return {
                "vehicle_id": vehicle_id,
                "service_date": service_date,
                "description": description,
                "status": status,
                "inventory_items": self.selected_items,  # Add inventory items
            }
        except ValueError as e:
            QMessageBox.critical(self, "Validation Error", str(e))
            raise

    def select_inventory_items(self):
        """Open dialog to select inventory items."""
        dialog = InventoryItemsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_items = dialog.get_selected_items()
            self.update_inventory_items_table()

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

    def accept(self) -> None:
        """Override accept to add validation."""
        try:
            self.get_data()  # Validate data before accepting
            super().accept()
        except ValueError:
            # Error message already shown by get_data()
            pass


class JobCardGUI(QWidget):
    """JobCard GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the JobCard GUI."""
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

        self.jobcard_view = JobCardView(model=JobCard)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Job Card Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search job cards...")
        self.search_input.textChanged.connect(self.search_jobcards)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Vehicle ID", "Service Date", "Description"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_jobcards)

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

        # JobCard table
        self.jobcard_table = QTableWidget()
        self.jobcard_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.jobcard_table.setAlternatingRowColors(True)
        self.jobcard_table.setStyleSheet("""
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
        self.jobcard_table.verticalHeader().setVisible(False)
        self.jobcard_table.horizontalHeader().setVisible(False)
        self.jobcard_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.jobcard_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.jobcard_table.horizontalHeader().setStretchLastSection(True)
        self.jobcard_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table_layout.addWidget(self.jobcard_table)
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
            ("Load Job Cards", self.load_jobcards),
            ("Add Job Card", self.add_jobcard),
            ("Update Job Card", self.update_jobcard),
            ("Delete Job Card", self.delete_jobcard),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        # Add a "Generate PDF" button to the button frame
        generate_pdf_button = QPushButton("Generate PDF")
        generate_pdf_button.clicked.connect(self.generate_pdf)
        button_layout.addWidget(generate_pdf_button)

        main_layout.addWidget(button_frame)

        self.load_jobcards()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def load_jobcards(self) -> None:
        """Load job cards from the database and display them in the table."""
        try:
            with Session(engine) as session:
                jobcards = self.jobcard_view.read_all(db_session=session)
                self.jobcard_table.setRowCount(len(jobcards) + 1)
                self.jobcard_table.setColumnCount(5)
                self.jobcard_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Vehicle ID",
                        "Service Date",
                        "Description",
                    ]
                )

                # Set column names in the first row
                column_names = [
                    "ID",
                    "Vehicle ID",
                    "Service Date",
                    "Description",
                ]
                for col, name in enumerate(column_names):
                    item = QTableWidgetItem(name)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.jobcard_table.setItem(0, col, item)

                # Set the height of the first row
                self.jobcard_table.setRowHeight(0, 40)

                for row, jobcard in enumerate(jobcards, start=1):
                    self.jobcard_table.setItem(
                        row, 0, QTableWidgetItem(str(jobcard.id))
                    )
                    self.jobcard_table.setItem(
                        row, 1, QTableWidgetItem(str(jobcard.vehicle_id))
                    )
                    self.jobcard_table.setItem(
                        row, 2, QTableWidgetItem(str(jobcard.service_date))
                    )
                    self.jobcard_table.setItem(
                        row, 3, QTableWidgetItem(jobcard.description)
                    )

                # Adjust column widths
                self.jobcard_table.resizeColumnsToContents()
                self.jobcard_table.horizontalHeader().setStretchLastSection(
                    True
                )
                self.jobcard_table.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.Stretch
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load job cards: {e!s}"
            )

    def add_jobcard(self) -> None:
        """Add a new job card to the database."""
        dialog = JobCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                with Session(engine) as session:
                    new_jobcard = JobCard(
                        vehicle_id=data["vehicle_id"],
                        service_date=datetime.strptime(
                            data["service_date"], "%Y-%m-%d"
                        ),
                        description=data["description"],
                        status=data["status"],  # Add status field
                        total_amount=0.0,  # Add a default value for total_amount
                    )
                    self.jobcard_view.create(
                        db_session=session, record=new_jobcard
                    )
                    QMessageBox.information(
                        self, "Success", "Job card added successfully!"
                    )
                    self.load_jobcards()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add job card: {e!s}"
                )

    def update_jobcard(self) -> None:
        """Update an existing job card."""
        selected_row = self.jobcard_table.currentRow()
        if selected_row <= 0:  # 0 is header row
            QMessageBox.warning(
                self, "Warning", "Please select a job card to update."
            )
            return

        try:
            jobcard_id = int(self.jobcard_table.item(selected_row, 0).text())

            # Fetch the current job card data
            with Session(engine) as session:
                current_jobcard = self.jobcard_view.read_by_id(
                    db_session=session, record_id=jobcard_id
                )

                if not current_jobcard:
                    QMessageBox.warning(self, "Error", "Job card not found.")
                    return

                # Create dialog with current data
                dialog = JobCardDialog(self, current_jobcard)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()

                    # Update the job card
                    current_jobcard.vehicle_id = data["vehicle_id"]
                    current_jobcard.service_date = datetime.strptime(
                        data["service_date"], "%Y-%m-%d"
                    )
                    current_jobcard.description = data["description"]

                    self.jobcard_view.update(
                        db_session=session,
                        record_id=jobcard_id,
                        record=current_jobcard,
                    )

                    QMessageBox.information(
                        self, "Success", "Job card updated successfully!"
                    )
                    self.load_jobcards()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update job card: {e!s}"
            )

    def delete_jobcard(self) -> None:
        """Delete a job card from the database."""
        try:
            selected_row = self.jobcard_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a job card to delete."
                )
                return

            item = self.jobcard_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected job card ID is invalid."
                )
                return
            jobcard_id = item.text()

            confirmation = QMessageBox.question(
                self,
                "Delete Job Card",
                "Are you sure you want to delete this job card?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.jobcard_view.delete(
                        db_session=session, record_id=int(jobcard_id)
                    )
                    QMessageBox.information(
                        self, "Success", "Job card deleted successfully!"
                    )
                    self.load_jobcards()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete job card: {e!s}"
            )

    def search_jobcards(self) -> None:
        """Filter job cards based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.jobcard_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "vehicle id":
                    cell_text = self.jobcard_table.item(row, 1)
                elif criteria == "service date":
                    cell_text = self.jobcard_table.item(row, 2)
                elif criteria == "description":
                    cell_text = self.jobcard_table.item(row, 3)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.jobcard_table.setRowHidden(row, not show_row)

    def generate_pdf(self) -> None:
        """Generate PDF for the selected job card."""
        selected_row = self.jobcard_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Warning", "Please select a job card to generate PDF."
            )
            return

        item = self.jobcard_table.item(selected_row, 0)
        if item is None:
            QMessageBox.warning(
                self, "Warning", "Selected job card ID is invalid."
            )
            return

        jobcard_id = int(item.text())

        try:
            with Session(engine) as session:
                # Get job card with related inventory items
                jobcard = self.jobcard_view.read_by_id(
                    db_session=session, record_id=jobcard_id
                )

                if not jobcard:
                    raise ValueError("Job card not found")

                # Get inventory items
                inventory_items = session.exec(
                    select(InventoryEstimate).where(
                        InventoryEstimate.estimate_id.in_(
                            [est.id for est in jobcard.estimates]
                        )
                    )
                ).all()

                # Generate PDF
                filename = f"jobcard_{jobcard_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                generate_jobcard_pdf(jobcard, inventory_items, filename)

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

    def setup_buttons(self):
        """Setup button connections."""
        self.update_button.clicked.connect(self.update_job_card_clicked)

    def update_job_card_clicked(self):
        """Handle the update job card button click."""
        selected_rows = self.jobcard_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(
                self, "Warning", "Please select a job card to update."
            )
            return

        # Get the selected row index
        row_index = selected_rows[0].row()

        # Get data from the selected row
        job_card_id = self.jobcard_table.item(row_index, 0).text()
        customer_id = self.jobcard_table.item(row_index, 1).text()
        vehicle_id = self.jobcard_table.item(row_index, 2).text()
        description = self.jobcard_table.item(row_index, 3).text()
        status = self.jobcard_table.item(row_index, 4).text()
        date_created = self.jobcard_table.item(row_index, 5).text()

        # Populate input fields with selected data
        self.customer_id_input.setText(customer_id)
        self.vehicle_id_input.setText(vehicle_id)
        self.description_input.setText(description)
        self.status_input.setCurrentText(status)

        # Store the job card ID for use in the actual update operation
        self.selected_job_card_id = job_card_id

        # You might want to change the add button text to indicate update mode
        self.add_button.setText("Update Job Card")
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(
            lambda: self.perform_update(job_card_id)
        )

    def perform_update(self, job_card_id):
        """Perform the actual update operation."""
        try:
            # Get values from input fields
            customer_id = self.customer_id_input.text()
            vehicle_id = self.vehicle_id_input.text()
            description = self.description_input.text()
            status = self.status_input.currentText()

            # Update the job card in the database
            with JobCardDB() as db:
                db.update_job_card(
                    job_card_id, customer_id, vehicle_id, description, status
                )

            # Reset the form and refresh the table
            self.clear_input_fields()
            self.load_job_cards()
            self.add_button.setText("Add Job Card")
            self.add_button.clicked.disconnect()
            self.add_button.clicked.connect(self.add_job_card)

            QMessageBox.information(
                self, "Success", "Job card updated successfully!"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update job card: {e!s}"
            )

    def clear_input_fields(self):
        """Clear all input fields."""
        self.customer_id_input.clear()
        self.vehicle_id_input.clear()
        self.description_input.clear()
        self.status_input.setCurrentIndex(0)


def generate_jobcard_pdf(jobcard, inventory_items, filename):
    """Generate PDF for a job card."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Header
    elements.append(Paragraph(f"Job Card #{jobcard.id}", styles["Title"]))
    elements.append(
        Paragraph(f"Date: {jobcard.service_date}", styles["Normal"])
    )

    # Job Card Details
    data = [
        ["Vehicle ID:", str(jobcard.vehicle_id)],
        ["Description:", jobcard.description],
    ]

    # Create table
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)


if __name__ == "__main__":
    app = QApplication([])
    window = JobCardGUI()
    window.show()
    app.exec()
