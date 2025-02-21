"""Base GUI Module.

Description:
- This module provides the base GUI components and common imports for other GUI modules.

"""

# Define a constant for the background color
BACKGROUND_COLOR = "white"

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BaseGUI(QWidget):
    """Base GUI Class."""

    def __init__(self, parent=None) -> None:
        """Initialize the Base GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.all_items = []
        self.filtered_items = []

        self.apply_styles()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Search Section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.search_items)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(self.get_search_criteria())
        self.search_criteria.currentTextChanged.connect(self.search_items)

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_criteria)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Buttons container
        buttons_layout = QHBoxLayout()

        # Back button (left aligned)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Add Customer button (right aligned)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """)

        # Add buttons to the layout
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()  # This creates space between the buttons
        buttons_layout.addWidget(add_button)

        main_layout.addLayout(buttons_layout)

        # Table Frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.NoFrame)
        table_layout = QVBoxLayout(table_frame)

        # Set minimum size for table frame
        table_frame.setMinimumHeight(300)
        table_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.customer_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid black;
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                outline: 0;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
                border: none;
                outline: none;
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
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.horizontalHeader().setVisible(False)
        self.customer_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.customer_table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )
        self.customer_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.customer_table.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.customer_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.customer_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_table.itemSelectionChanged.connect(self.on_row_selected)
        table_layout.addWidget(self.customer_table)
        main_layout.addWidget(table_frame)

        # Ensure column count is set before calculating default section size
        self.customer_table.setColumnCount(5)  # Set the number of columns
        self.customer_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.customer_table.horizontalHeader().setDefaultSectionSize(
            self.customer_table.width() // self.customer_table.columnCount()
        )

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

    def apply_styles(self, widget=None):
        """Apply common styles."""
        style = """
            QMainWindow {
                background-color: white;
            }
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel#headerLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 20px;
            }
            /* ...rest of the styles... */
        """
        target = widget if widget else self
        target.setStyleSheet(style)

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.parent_widget and isinstance(self.parent_widget, QMainWindow):
            # Implement the logic to navigate back to the home page
            pass
        else:
            QMessageBox.warning(
                self, "Error", "Parent widget is not a QMainWindow."
            )

    def add(self) -> None:
        """Add a new customer to the database."""
        # Implement the logic to add a new customer
        pass

    def search_items(self) -> None:
        """Filter items based on search criteria across all data."""
        search_text = self.search_input.text().lower()
        criteria = self.search_criteria.currentText().lower()

        # Filter all items
        self.filtered_items = self.all_items.copy()
        if search_text:
            self.filtered_items = [
                item
                for item in self.all_items
                if (
                    (
                        criteria == "id"
                        and search_text in str(item["ID"]).lower()
                    )
                    or (
                        criteria == "name"
                        and search_text in item["Name"].lower()
                    )
                    or (
                        criteria == "mobile"
                        and search_text in item["Mobile"].lower()
                    )
                    or (
                        criteria == "email"
                        and search_text in item["Email"].lower()
                    )
                    or (
                        criteria == "address"
                        and search_text in item["Address"].lower()
                    )
                )
            ]

        # Reload the table with filtered data
        self.load_items()

    def load_items(self) -> None:
        """Load items into the table."""
        self.customer_table.setRowCount(
            len(self.filtered_items) + 1
        )  # +1 for header
        self.customer_table.setColumnCount(5)

        # Set headers
        headers = ["ID", "Name", "Mobile", "Email", "Address"]
        for col, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.customer_table.setItem(0, col, item)

        # Populate data
        for row, item in enumerate(self.filtered_items, start=1):
            self.customer_table.setItem(
                row, 0, QTableWidgetItem(str(item["ID"]))
            )
            self.customer_table.setItem(row, 1, QTableWidgetItem(item["Name"]))
            self.customer_table.setItem(
                row, 2, QTableWidgetItem(item["Mobile"])
            )
            self.customer_table.setItem(
                row, 3, QTableWidgetItem(item["Email"])
            )
            self.customer_table.setItem(
                row, 4, QTableWidgetItem(item["Address"])
            )

        # Maintain table appearance
        self.customer_table.resizeColumnsToContents()
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Set consistent row heights
        row_height = 40
        for row in range(self.customer_table.rowCount()):
            self.customer_table.setRowHeight(row, row_height)

    def show_context_menu(self, position):
        """Show context menu for table row."""
        row = self.customer_table.rowAt(position.y())
        if row >= 0:  # Ensure a valid row is selected
            self.customer_table.selectRow(row)
            context_menu = QMenu(self)
            context_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 10px;
                    min-width: 150px;
                }
                QMenu::item {
                    background-color: aqua;
                    padding: 10px 20px;
                    color: black;
                    border-radius: 5px;
                    margin: 5px;
                    font-size: 14px;
                }
                QMenu::item:hover {
                    background-color: #f2f2f2;  /* Change this to your desired hover color */
                    color: red;                /* Change text color on hover */
                }
                QMenu::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background: #cccccc;
                    margin: 5px;
                }
            """)

            # Create styled update action
            update_action = context_menu.addAction("✏️  Update")
            update_action.setStatusTip("Update selected item")

            context_menu.addSeparator()

            # Create styled delete action
            delete_action = context_menu.addAction("🗑️  Delete")
            delete_action.setStatusTip("Delete selected item")

            # Position the context menu to appear next to the cursor
            action = context_menu.exec(
                self.customer_table.mapToGlobal(position)
            )
            if action == update_action:
                self.update_item()
            elif action == delete_action:
                self.delete_item()

    def update_item(self):
        """Update the selected item."""
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Update", "Update item functionality"
            )

    def delete_item(self):
        """Delete the selected item."""
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            QMessageBox.information(
                self, "Delete", "Delete item functionality"
            )

    def on_row_selected(self):
        """Handle row selection changes."""
        selected_items = self.customer_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            self.customer_table.selectRow(selected_row)
            for col in range(self.customer_table.columnCount()):
                item = self.customer_table.item(selected_row, col)
                if item:
                    item.setBackground(Qt.GlobalColor.lightGray)
        else:
            self.clear_row_highlight()

    def clear_row_highlight(self):
        """Clear row highlight."""
        for row in range(self.customer_table.rowCount()):
            for col in range(self.customer_table.columnCount()):
                item = self.customer_table.item(row, col)
                if item:
                    item.setBackground(Qt.GlobalColor.white)

    def previous_page(self) -> None:
        """Load the previous page of items."""
        # Implement the logic to load the previous page
        pass

    def next_page(self) -> None:
        """Load the next page of items."""
        # Implement the logic to load the next page
        pass

    def add_page_button(self, page_num: int) -> None:
        """Add a single page button."""
        button = QPushButton(str(page_num))
        button.setFixedSize(40, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumWidth(40)
        button.setMaximumWidth(40)

        if page_num == 1:  # Assuming current page is 1 for demonstration
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
                    background-color: skyblue;
                }
            """)

        button.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
        self.page_buttons_layout.addWidget(button)

    def go_to_page(self, page_number):
        """Navigate to specific page number."""
        # Implement the logic to navigate to a specific page
        pass

    # def get_search_criteria(self) -> list[str]:
    #     """Get search criteria for the model.

    #     Override this method in child classes to provide model-specific search criteria.
    #     """
    #     return ["ID", "Name", "Mobile", "Email", "Address"]
