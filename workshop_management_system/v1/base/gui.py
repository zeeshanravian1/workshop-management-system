"""Base GUI Module.

Description:
- This module provides base GUI components for the application.

"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class BaseDialog(QDialog):
    """Base dialog for data entry."""

    def __init__(self, parent=None, data: dict | None = None) -> None:
        """Initialize the Base Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Details")
        self.setMinimumWidth(400)
        self.setStyleSheet(
            """
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
        """
        )

        self.form_layout = QFormLayout(self)
        self.setup_form()

        # Add OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        self.form_layout.addWidget(self.buttons)

    def setup_form(self):
        """Setup form fields - to be implemented by subclasses."""
        raise NotImplementedError

    def validate(self):
        """Validate form inputs - to be implemented by subclasses."""
        raise NotImplementedError


class BaseManagementGUI(QWidget):
    """Base class for management GUIs."""

    def __init__(self, parent=None, page_size: int = 15) -> None:
        """Initialize the Base Management GUI."""
        super().__init__(parent)
        self.parent_widget = parent
        self.current_page = 1
        self.page_size: int = page_size

        # Add base styling
        self.setStyleSheet(
            """
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
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
                background-color: white;
                border: none;
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
            QLabel {
                color: black;
            }
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                color: black;
                border-radius: 4px;
                margin: 2px 5px;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #cccccc;
                margin: 5px 0px;
            }
        """
        )

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the base UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.setup_header(main_layout)

        # Search Section
        self.setup_search(main_layout)

        # Buttons Section
        self.setup_buttons(main_layout)

        # Table Section
        self.setup_table(main_layout)

        # Pagination Section
        self.setup_pagination(main_layout)

    def setup_header(self, main_layout) -> None:
        """Setup header section."""
        header_layout = QHBoxLayout()
        title_label = QLabel("Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

    def setup_search(self, main_layout) -> None:
        """Setup search section."""
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_criteria = QComboBox()

        search_layout.addWidget(QLabel("Search by:"))
        search_layout.addWidget(self.search_criteria)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

    def setup_buttons(self, main_layout) -> None:
        """Setup buttons section."""
        buttons_layout = QHBoxLayout()

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_to_home)
        back_button.setStyleSheet(
            """
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """
        )

        # Add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_record)
        add_button.setStyleSheet(
            """
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """
        )

        # Update button
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_record)
        update_button.setStyleSheet(
            """
            QPushButton {
                background-color: skyblue;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """
        )

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_record)
        delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4444;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """
        )

        # Add buttons to layout
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(update_button)
        buttons_layout.addWidget(delete_button)

        main_layout.addLayout(buttons_layout)

    def setup_table(self, main_layout) -> None:
        """Setup table section."""
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.NoFrame)
        table_layout = QVBoxLayout(table_frame)

        self.table = QTableWidget()
        self.setup_table_properties()

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame)

    def setup_table_properties(self) -> None:
        """Setup table widget properties."""
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def setup_pagination(self, main_layout) -> None:
        """Setup pagination section."""
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setSpacing(5)

        # Previous button styling
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setStyleSheet(
            """
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """
        )

        # Page number buttons container
        self.page_buttons_layout = QHBoxLayout()
        self.page_buttons_layout.setSpacing(5)

        # Next button styling
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet(
            """
            QPushButton {
                background-color: skyblue;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ADD8E6;
            }
        """
        )

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addLayout(self.page_buttons_layout)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(pagination_frame)

    def back_to_home(self) -> None:
        """Navigate back to home."""
        if self.parent_widget:
            self.parent_widget.back_to_home()

    def add_record(self):
        """Add new record - to be implemented by subclasses."""
        raise NotImplementedError

    def update_record(self):
        """Update record - to be implemented by subclasses."""
        raise NotImplementedError

    def delete_record(self):
        """Delete record - to be implemented by subclasses."""
        raise NotImplementedError

    def load_records(self):
        """Load records - to be implemented by subclasses."""
        raise NotImplementedError

    def previous_page(self) -> None:
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_records()

    def next_page(self) -> None:
        """Go to next page."""
        self.current_page += 1
        self.load_records()
