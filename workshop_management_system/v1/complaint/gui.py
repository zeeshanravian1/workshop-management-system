"""Complaint GUI Module."""

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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session, select

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.complaint.model import Complaint
from workshop_management_system.v1.complaint.view import ComplaintView
from workshop_management_system.v1.customer.gui import CustomerDialog
from workshop_management_system.v1.customer.model import Customer


class CustomerComboBox(QComboBox):
    """Custom ComboBox for customer selection."""

    def __init__(self, parent=None) -> None:
        """Initialize CustomerComboBox."""
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
                background-color: white;
            }
            QComboBox::drop-down {
                width: 30px;
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                backgroundcolor: silver;
                color: green;
                width: 12px;
                height: 12px;
                border: 2px solid #4CAF50;
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
                margin-top: -5px;
            }
        """)
        self.customer_ids = []
        self.load_customers()
        self.currentIndexChanged.connect(self.check_new_customer)

    def load_customers(self) -> None:
        """Load customers into combo box."""
        try:
            with Session(engine) as session:
                customers = session.exec(select(Customer)).all()
                self.clear()
                self.customer_ids.clear()

                self.addItem("Select a customer...")
                self.customer_ids.append(None)
                self.addItem("Add new customer...")
                self.customer_ids.append("new")

                for customer in customers:
                    self.customer_ids.append(customer.id)
                    display_text = (
                        f"{customer.name} ({customer.mobile_number})"
                    )
                    self.addItem(display_text)
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load customers: {e!s}"
            )

    def get_selected_customer_id(self) -> int | str | None:
        """Get the ID of the selected customer."""
        current_index = self.currentIndex()
        if current_index == 1:  # Add new customer
            return "new"
        if current_index > 1 and current_index < len(self.customer_ids):
            return self.customer_ids[current_index]
        return None

    def check_new_customer(self) -> None:
        """Check if 'Add new customer...' is selected and show dialog."""
        if self.currentIndex() == 1:
            customer_id = self.parentWidget().parentWidget().add_new_customer()
            if customer_id:
                self.load_customers()
                self.setCurrentIndex(self.customer_ids.index(customer_id))


class ComplaintGUI(QWidget):
    """Complaint GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Complaint GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        # Add pagination dictionary to match base model
        self.pagination = {
            "current_page": 1,
            "limit": 15,
            "total_pages": 0,
            "total_records": 0,
            "next_record_id": None,
            "previous_record_id": None,
            "records": [],
        }
        # Keep compatibility properties
        self.page_size = self.pagination["limit"]
        self.current_page = self.pagination["current_page"]
        self.all_complaints = []
        self.filtered_complaints = []

        # Update theme to match customer/vehicle GUI
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
                outline: 0;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
                border: none;
                outline: none;
            }
        """)

        self.complaint_view = ComplaintView(model=Complaint)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Complaint Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search complaints...")
        self.search_input.textChanged.connect(self.search_complaints)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(
            ["Customer", "Description", "Priority", "Status"]
        )
        self.search_criteria.currentTextChanged.connect(self.search_complaints)

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
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)  # Remove internal margins

        # Complaints table
        self.complaint_table = QTableWidget()
        self.complaint_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.complaint_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.complaint_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
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
        self.complaint_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.complaint_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.complaint_table.horizontalHeader().setStretchLastSection(True)
        self.complaint_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.complaint_table.verticalHeader().setVisible(False)
        self.complaint_table.horizontalHeader().setVisible(False)

        # Safer way to handle table stretching
        header = self.complaint_table.horizontalHeader()
        header.setStretchLastSection(True)

        table_layout.addWidget(self.complaint_table)
        main_layout.addWidget(table_frame, 1)  # Use stretch factor 1

        # Button Frame
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.Shape.StyledPanel)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # CRUD Buttons
        buttons = [
            ("Load Complaints", self.load_complaints),
            ("Add Complaint", self.add_complaint),
            ("Update Complaint", self.update_complaint),
            ("Delete Complaint", self.delete_complaint),
        ]

        for text, handler in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        main_layout.addWidget(button_frame)

        # Add pagination frame
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

        self.load_complaints()

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def create_input_dialog(
        self, title: str, complaint: Complaint | None = None
    ) -> tuple[QDialog, dict]:
        """Create a dialog for complaint input."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        inputs = {}

        # Customer selection
        inputs["customer"] = CustomerComboBox(dialog)
        if complaint:
            inputs["customer"].setCurrentIndex(
                inputs["customer"].customer_ids.index(complaint.customer_id)
            )
        layout.addRow("Customer:", inputs["customer"])

        # Description
        inputs["description"] = QTextEdit(dialog)
        inputs["description"].setMaximumHeight(100)
        if complaint:
            inputs["description"].setText(complaint.description)
        layout.addRow("Description:", inputs["description"])

        # Priority
        inputs["priority"] = QComboBox(dialog)
        inputs["priority"].addItems(["Low", "Medium", "High"])
        if complaint:
            inputs["priority"].setCurrentText(complaint.priority)
        layout.addRow("Priority:", inputs["priority"])

        # Status
        inputs["status"] = QComboBox(dialog)
        inputs["status"].addItems(["New", "In Progress", "Resolved", "Closed"])
        if complaint:
            inputs["status"].setCurrentText(complaint.status)
        layout.addRow("Status:", inputs["status"])

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog, inputs

    def add_new_customer(self) -> int | None:
        """Add a new customer to the database."""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not all(data.values()):
                QMessageBox.warning(
                    self, "Invalid Input", "All fields are required!"
                )
                return None

            try:
                with Session(engine) as session:
                    new_customer = Customer(**data)
                    session.add(new_customer)
                    session.commit()
                    return new_customer.id
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add customer: {e!s}"
                )
                return None
        return None

    def load_complaints(self, refresh_all=True) -> None:
        """Load complaints with pagination."""
        try:
            with Session(engine) as session:
                if refresh_all:
                    self.all_complaints = self.complaint_view.read_all(
                        db_session=session
                    )
                    self.filtered_complaints = self.all_complaints.copy()

                total_records = len(self.filtered_complaints)
                total_pages = (
                    total_records + self.pagination["limit"] - 1
                ) // self.pagination["limit"]

                # Update pagination state
                self.pagination.update(
                    {
                        "total_records": total_records,
                        "total_pages": total_pages,
                    }
                )

                # Calculate page data
                start_idx = (
                    self.pagination["current_page"] - 1
                ) * self.pagination["limit"]
                end_idx = start_idx + self.pagination["limit"]
                current_page_records = self.filtered_complaints[
                    start_idx:end_idx
                ]
                self.pagination["records"] = current_page_records

                # Update next/previous record IDs
                if end_idx < total_records:
                    self.pagination["next_record_id"] = (
                        self.filtered_complaints[end_idx].id
                    )
                else:
                    self.pagination["next_record_id"] = None

                if start_idx > 0:
                    self.pagination["previous_record_id"] = (
                        self.filtered_complaints[start_idx - 1].id
                    )
                else:
                    self.pagination["previous_record_id"] = None

                # Update table content
                self._update_table_data(current_page_records)

                # Update pagination UI
                self.update_pagination_buttons(total_pages)
                self.prev_button.setEnabled(
                    self.pagination["previous_record_id"] is not None
                )
                self.next_button.setEnabled(
                    self.pagination["next_record_id"] is not None
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load complaints: {e!s}"
            )

    def on_row_selected(self) -> None:
        """Handle row selection."""
        selected_items = self.complaint_table.selectedItems()
        if not selected_items:
            return

        # Get the first selected item's row (they'll all be from same row due
        # to SelectRows behavior)
        row = selected_items[0].row()

        # Skip if header row is selected
        if row == 0:
            self.complaint_table.clearSelection()
            return

        # Optional: Scroll to make the selected row visible
        self.complaint_table.scrollToItem(selected_items[0])

        # Show a popup with row info including description
        customer = self.complaint_table.item(row, 1).text()
        description = self.complaint_table.item(row, 2).text()
        status = self.complaint_table.item(row, 4).text()
        QMessageBox.information(
            self,
            "Selected Complaint",
            f"Customer: {customer}\n"
            f"Description: {description}\n"
            f"Status: {status}",
            QMessageBox.StandardButton.Ok,
        )

    def add_complaint(self) -> None:
        """Add a new complaint to the database."""
        try:
            dialog, inputs = self.create_input_dialog("Add Complaint")

            if dialog.exec() == QDialog.DialogCode.Accepted:
                customer_id = inputs["customer"].get_selected_customer_id()
                if customer_id == "new":
                    customer_id = self.add_new_customer()
                    if not customer_id:
                        return
                    inputs["customer"].load_customers()
                    inputs["customer"].setCurrentIndex(
                        inputs["customer"].customer_ids.index(customer_id)
                    )
                elif not customer_id:
                    QMessageBox.critical(
                        self, "Error", "Please select a customer."
                    )
                    return

                with Session(engine) as session:
                    new_complaint = Complaint(
                        description=inputs["description"].toPlainText(),
                        priority=inputs["priority"].currentText(),
                        status=inputs["status"].currentText(),
                        customer_id=customer_id,
                    )
                    self.complaint_view.create(
                        db_session=session, record=new_complaint
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint added successfully!"
                    )
                    self.load_complaints()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add complaint: {e!s}"
            )

    def update_complaint(self) -> None:
        """Update an existing complaint."""
        try:
            selected_row = self.complaint_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a complaint to update."
                )
                return

            item = self.complaint_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected complaint ID is invalid."
                )
                return
            complaint_id = int(item.text())

            with Session(engine) as session:
                complaint_obj = self.complaint_view.read_by_id(
                    db_session=session, record_id=complaint_id
                )
                if not complaint_obj:
                    QMessageBox.warning(self, "Error", "Complaint not found.")
                    return

                dialog, inputs = self.create_input_dialog(
                    "Update Complaint", complaint_obj
                )

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    customer_id = inputs["customer"].get_selected_customer_id()
                    if not customer_id:
                        QMessageBox.critical(
                            self, "Error", "Please select a customer."
                        )
                        return

                    complaint_obj.description = inputs[
                        "description"
                    ].toPlainText()
                    complaint_obj.priority = inputs["priority"].currentText()
                    complaint_obj.status = inputs["status"].currentText()
                    complaint_obj.customer_id = customer_id

                    self.complaint_view.update(
                        db_session=session,
                        record_id=complaint_id,
                        record=complaint_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint updated successfully!"
                    )
                    self.load_complaints()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update complaint: {e!s}"
            )

    def delete_complaint(self) -> None:
        """Delete a complaint from the database."""
        try:
            selected_row = self.complaint_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a complaint to delete."
                )
                return

            item = self.complaint_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected complaint ID is invalid."
                )
                return
            complaint_id = int(item.text())

            confirmation = QMessageBox.question(
                self,
                "Delete Complaint",
                "Are you sure you want to delete this complaint?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.complaint_view.delete(
                        db_session=session, record_id=complaint_id
                    )
                    QMessageBox.information(
                        self, "Success", "Complaint deleted successfully!"
                    )
                    self.load_complaints()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete complaint: {e!s}"
            )

    def search_complaints(self) -> None:
        """Filter complaints based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        # Filter all complaints
        self.filtered_complaints = self.all_complaints.copy()
        if search_text:
            self.filtered_complaints = []
            with Session(engine) as session:
                for complaint in self.all_complaints:
                    match = False
                    if criteria == "customer":
                        customer = session.get(Customer, complaint.customer_id)
                        if customer and search_text in customer.name.lower():
                            match = True
                    elif criteria == "description":
                        if search_text in complaint.description.lower():
                            match = True
                    elif criteria == "priority":
                        if search_text in complaint.priority.lower():
                            match = True
                    elif criteria == "status":
                        if search_text in complaint.status.lower():
                            match = True

                    if match:
                        self.filtered_complaints.append(complaint)

        # Reset pagination
        self.pagination["current_page"] = 1
        self.current_page = 1  # Keep in sync
        self.pagination["total_records"] = len(self.filtered_complaints)

        # Reload the table with filtered data
        self.load_complaints(refresh_all=False)

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
        """Load the next page of complaints."""
        if self.pagination["next_record_id"] is not None:
            self.pagination["current_page"] += 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_complaints(refresh_all=False)

    def previous_page(self) -> None:
        """Load the previous page of complaints."""
        if self.pagination["previous_record_id"] is not None:
            self.pagination["current_page"] -= 1
            self.current_page = self.pagination["current_page"]  # Keep in sync
            self.load_complaints(refresh_all=False)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to specific page number."""
        if (
            1 <= page_number <= self.pagination["total_pages"]
            and page_number != self.pagination["current_page"]
        ):
            self.pagination["current_page"] = page_number
            self.current_page = page_number  # Keep in sync
            self.load_complaints(refresh_all=False)

    def _update_table_data(self, records):
        """Update table data while preserving table properties."""
        self.complaint_table.setRowCount(len(records) + 1)
        self.complaint_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Customer", "Description", "Priority", "Status"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.complaint_table.setItem(0, col, item)

        # Populate data
        for row, complaint in enumerate(records, start=1):
            with Session(engine) as session:
                customer = session.get(Customer, complaint.customer_id)
                self.complaint_table.setItem(
                    row, 0, QTableWidgetItem(str(complaint.id))
                )
                self.complaint_table.setItem(
                    row, 1, QTableWidgetItem(customer.name if customer else "")
                )
                self.complaint_table.setItem(
                    row, 2, QTableWidgetItem(complaint.description)
                )
                self.complaint_table.setItem(
                    row, 3, QTableWidgetItem(complaint.priority)
                )
                self.complaint_table.setItem(
                    row, 4, QTableWidgetItem(complaint.status)
                )

        # Maintain table appearance
        self.complaint_table.resizeColumnsToContents()
        self.complaint_table.horizontalHeader().setStretchLastSection(True)
        self.complaint_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.complaint_table.rowCount()):
            self.complaint_table.setRowHeight(row, row_height)


if __name__ == "__main__":
    app = QApplication([])
    window = ComplaintGUI()
    window.show()
    app.exec()
