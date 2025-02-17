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
    QSizePolicy,
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
                border: 2px solid #87CEEB;
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
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                background-color: #87CEEB;
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
                min-width: 125px;
                margin: 0px;
            }
            QTableWidget {
                background-color: white;
                color: black;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item:alternate {
                background-color: #f5f5f5;
            }
            QTableWidget::item {
                background-color: white;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #90EE90;  /* Light green */
                color: black;
            }
            QTableWidget::item:selected:active {
                background-color: #87CEEB;  /* Darker green when active */
                color: white;
            }
            QLabel {
                color: black;
            }
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: black;
            }
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
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
        self.complaint_table.setAlternatingRowColors(
            False
        )  # Disable alternating colors
        self.complaint_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.complaint_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ddd;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #87CEEB;
                color: white;
            }
        """)
        self.complaint_table.verticalHeader().setVisible(False)
        self.complaint_table.horizontalHeader().setVisible(False)
        self.complaint_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.complaint_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.complaint_table.itemSelectionChanged.connect(self.on_row_selected)

        # Set the horizontal header to stretch
        header = self.complaint_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )  # Key change here

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

    def load_complaints(self) -> None:
        """Load complaints from database."""
        try:
            with Session(engine) as session:
                complaints = self.complaint_view.read_all(db_session=session)
                self.complaint_table.setRowCount(len(complaints) + 1)
                self.complaint_table.setColumnCount(5)

                # Hide the default headers
                self.complaint_table.horizontalHeader().hide()
                self.complaint_table.verticalHeader().hide()

                # Adjusted column widths - made status even shorter
                self.complaint_table.setColumnWidth(0, 60)  # ID
                self.complaint_table.setColumnWidth(1, 160)  # Customer
                self.complaint_table.setColumnWidth(
                    2, 600
                )  # Description (even longer)
                self.complaint_table.setColumnWidth(3, 70)  # Priority
                self.complaint_table.setColumnWidth(
                    4, 40
                )  # Status (much shorter)

                # Connect selection changed signal
                self.complaint_table.itemSelectionChanged.connect(
                    self.on_row_selected
                )

                # Add header row as first row of table with grey background
                headers = [
                    "ID",
                    "Customer",
                    "Description",
                    "Priority",
                    "Status",
                ]
                for col, header in enumerate(headers):
                    item = QTableWidgetItem(header)
                    item.setBackground(
                        Qt.GlobalColor.lightGray
                    )  # Set grey background
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.complaint_table.setItem(0, col, item)

                # Set the height of the first row
                self.complaint_table.setRowHeight(0, 40)

                # Populate data rows with alternating colors
                for row, complaint in enumerate(complaints, start=1):
                    # Set background color for entire row
                    for col in range(5):
                        item = QTableWidgetItem()
                        if row % 2 == 0:
                            item.setBackground(Qt.GlobalColor.white)
                        else:
                            item.setBackground(Qt.GlobalColor.lightGray)
                        self.complaint_table.setItem(row, col, item)

                    # Now set the actual data
                    customer = session.get(Customer, complaint.customer_id)
                    self.complaint_table.item(row, 0).setText(
                        str(complaint.id)
                    )
                    self.complaint_table.item(row, 1).setText(
                        customer.name if customer else ""
                    )
                    self.complaint_table.item(row, 2).setText(
                        complaint.description
                    )
                    self.complaint_table.item(row, 3).setText(
                        complaint.priority
                    )
                    self.complaint_table.item(row, 4).setText(complaint.status)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load complaints: {e!s}"
            )

    def on_row_selected(self) -> None:
        """Handle row selection changes."""
        if self.complaint_table.selectedItems():
            current_row = self.complaint_table.currentRow()
            if current_row == 0:  # If header row is selected
                self.complaint_table.clearSelection()
            else:
                # Select entire row
                self.complaint_table.selectRow(current_row)

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
        """Filter complaints based on search criteria."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        for row in range(
            1, self.complaint_table.rowCount()
        ):  # Start from 1 to skip header
            show_row = True
            if search_text:
                cell_text = ""
                if criteria == "customer":
                    cell_text = self.complaint_table.item(row, 1)
                elif criteria == "description":
                    cell_text = self.complaint_table.item(row, 2)
                elif criteria == "priority":
                    cell_text = self.complaint_table.item(row, 3)
                elif criteria == "status":
                    cell_text = self.complaint_table.item(row, 4)

                if (
                    cell_text
                    and cell_text.text().lower().find(search_text) == -1
                ):
                    show_row = False

            self.complaint_table.setRowHidden(row, not show_row)


if __name__ == "__main__":
    app = QApplication([])
    window = ComplaintGUI()
    window.show()
    app.exec()
