"""Home GUI Module.

Description:
- This module provides the main GUI for navigating different sections of the
  application.

"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from workshop_management_system.core.load_models import load_all_models
from workshop_management_system.v1.customer.gui import CustomerGUI

load_all_models()


class HomeGUI(QMainWindow):
    """Home GUI Class."""

    def __init__(self) -> None:
        """Initialize the Home GUI."""
        super().__init__()
        self.setWindowTitle("Workshop Management System")
        self.setGeometry(100, 100, 1000, 600)  # Increased default width
        self.setMinimumSize(800, 600)  # Set minimum window size
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QPushButton {
                padding: 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                min-width: 250px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: #333;
            }
            QFrame {
                background-color: transparent;
                border-radius: 20px;
            }
        """)

        self.bar_text = "Powered by: NexAI"
        self.current_text = ""
        self.bar_label = None
        self.bar_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bar_text)

        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.create_home_page()

    def create_home_page(self) -> None:
        """Create the home page layout."""
        # Stop any existing timer
        if self.timer.isActive():
            self.timer.stop()

        # Clear the main layout
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Header container
        header_container = QVBoxLayout()
        header_container.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # Header
        welcome_label = QLabel("Workshop Management System")
        welcome_label.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_container.addWidget(welcome_label)

        # Description
        description_label = QLabel(
            "Manage your workshop operations efficiently"
        )
        description_label.setFont(QFont("Arial", 30))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_container.addWidget(description_label)

        self.main_layout.addLayout(header_container)

        # Main horizontal layout
        main_container = QHBoxLayout()

        # Left side - Image
        image_label = QLabel()
        pixmap = QPixmap("pic.jpg")
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_container.addWidget(image_label, 1)  # Stretch factor 1

        # Right side - Content
        content_container = QVBoxLayout()
        content_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Button container
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 0px;
            }
            QPushButton {
                padding: 20px;
                font-size: 16px;
                background-color: skyblue;
                color: white;
                border-radius: 5px;
                min-width: 180px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: skyblue;
                margin: 5px;
            }
        """)

        # Button grid layout
        button_layout = QGridLayout(button_frame)
        button_layout.setSpacing(15)
        button_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align buttons

        # Define buttons and their handlers
        buttons = [
            ("Customer Management", self.open_customer_gui),
            ("Vehicle Management", self.open_vehicle_gui),
            ("Job Card Management", self.open_job_card_gui),
            ("Estimate Management", self.open_estimate_gui),
            ("Payment Management", self.open_payment_gui),
            ("Inventory Management", self.open_inventory_gui),
            ("Supplier Management", self.open_supplier_gui),
            ("Complaint Management", self.open_complaint_gui),
        ]

        # Add buttons to grid
        for index, (text, handler) in enumerate(buttons):
            button = QPushButton(text)
            button.clicked.connect(handler)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            row = index // 2
            col = index % 2
            button_layout.addWidget(
                button, row, col, Qt.AlignmentFlag.AlignCenter
            )

        content_container.addWidget(button_frame, 1)

        # Bar container
        bar_container = QVBoxLayout()
        bar_container.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )
        self.bar_label = QLabel()
        self.bar_label.setFont(QFont("Arial", 14))
        self.bar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_text = ""  # Reset current text
        self.bar_index = 0
        bar_container.addWidget(self.bar_label)
        content_container.addLayout(bar_container)

        # Start the timer after creating the label
        self.timer.start(300)

        main_container.addLayout(content_container, 1)  # Stretch factor 1

        # Add main container to main layout
        self.main_layout.addLayout(main_container)

    def update_bar_text(self) -> None:
        """Update the bar text character by character infinitely."""
        try:
            if not self.bar_label or not self.bar_label.isVisible():
                self.timer.stop()
                return

            if self.bar_index < len(self.bar_text):
                self.current_text += self.bar_text[self.bar_index]
                self.bar_label.setText(self.current_text)
                self.bar_index += 1
            else:
                self.current_text = ""
                self.bar_label.setText("")
                self.bar_index = 0
                self.timer.stop()
                QTimer.singleShot(2000, self.restart_timer)

        except RuntimeError:
            self.timer.stop()

    def restart_timer(self):
        """Restart the timer."""
        try:
            if self.bar_label and self.bar_label.isVisible():
                self.timer.start(300)
        except RuntimeError:
            pass

    def open_customer_gui(self) -> None:
        """Open the Customer Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.customer_window = CustomerGUI(self)
        self.setCentralWidget(self.customer_window)

    def open_vehicle_gui(self) -> None:
        """Open the Vehicle Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.vehicle_window = VehicleGUI(self)
        self.setCentralWidget(self.vehicle_window)

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.jobcard_window = JobCardGUI(self)
        self.setCentralWidget(self.jobcard_window)

    def open_estimate_gui(self) -> None:
        """Open the Estimate Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.estimate_window = EstimateGUI(self)
        self.setCentralWidget(self.estimate_window)

    def open_payment_gui(self) -> None:
        """Open the Payment Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.payment_window = PaymentGUI(self)
        self.setCentralWidget(self.payment_window)

    def open_inventory_gui(self) -> None:
        """Open the Inventory Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.inventory_window = InventoryGUI(self)
        self.setCentralWidget(self.inventory_window)

    def open_supplier_gui(self) -> None:
        """Open the Supplier Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.supplier_window = SupplierGUI(self)
        self.setCentralWidget(self.supplier_window)

    def open_complaint_gui(self) -> None:
        """Open the Complaint Management GUI."""
        if self.timer.isActive():
            self.timer.stop()
        self.complaint_window = ComplaintGUI(self)
        self.setCentralWidget(self.complaint_window)

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
        if self.timer.isActive():
            self.timer.stop()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.create_home_page()


if __name__ == "__main__":
    app = QApplication([])
    window = HomeGUI()
    window.show()
    app.exec()
