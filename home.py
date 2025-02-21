"""Home GUI Module.

Description:
- This module provides the main GUI for navigating different sections of the
  application.

"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from workshop_management_system.v1.complaint.gui import ComplaintGUI
from workshop_management_system.v1.customer.gui import CustomerGUI
from workshop_management_system.v1.estimate.gui import EstimateGUI
from workshop_management_system.v1.inventory.gui import InventoryGUI
from workshop_management_system.v1.jobcard.gui import JobCardGUI
from workshop_management_system.v1.payment.gui import PaymentGUI
from workshop_management_system.v1.supplier.gui import SupplierGUI
from workshop_management_system.v1.vehicle.gui import VehicleGUI


class HomeGUI(QMainWindow):
    """Home GUI Class.

    Description:
    - This class provides the main GUI for navigating the application.

    """

    def __init__(self) -> None:
        """Initialize the Home GUI."""
        super().__init__()
        self.setWindowTitle("Workshop Management System")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                min-width: 200px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
                margin: 0px;
            }
            QLabel {
                color: #333;
            }
        """)

        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.create_home_page()

    def create_home_page(self) -> None:
        """Create the home page layout."""
        # Clear the main layout
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        # Header
        header_layout = QHBoxLayout()
        welcome_label = QLabel("Workshop Management System")
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(welcome_label)
        self.main_layout.addLayout(header_layout)

        # Description
        description_label = QLabel(
            "Powered by Nex AI"
        )
        description_label.setFont(QFont("Arial", 12))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(description_label)

        # Button container
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.Shape.StyledPanel)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        button_layout = QGridLayout(button_frame)
        button_layout.setSpacing(15)

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
            row = index // 2
            col = index % 2
            button_layout.addWidget(button, row, col)

        self.main_layout.addWidget(button_frame)

    def open_customer_gui(self) -> None:
        """Open the Customer Management GUI."""
        self.customer_window = CustomerGUI(self)
        self.setCentralWidget(self.customer_window)

    def open_vehicle_gui(self) -> None:
        """Open the Vehicle Management GUI."""
        self.vehicle_window = VehicleGUI(self)
        self.setCentralWidget(self.vehicle_window)

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        self.jobcard_window = JobCardGUI(self)
        self.setCentralWidget(self.jobcard_window)

    def open_estimate_gui(self) -> None:
        """Open the Estimate Management GUI."""
        self.estimate_window = EstimateGUI(self)
        self.setCentralWidget(self.estimate_window)

    def open_payment_gui(self) -> None:
        """Open the Payment Management GUI."""
        self.payment_window = PaymentGUI(self)
        self.setCentralWidget(self.payment_window)

    def open_inventory_gui(self) -> None:
        """Open the Inventory Management GUI."""
        self.inventory_window = InventoryGUI(self)
        self.setCentralWidget(self.inventory_window)

    def open_supplier_gui(self) -> None:
        """Open the Supplier Management GUI."""
        self.supplier_window = SupplierGUI(self)
        self.setCentralWidget(self.supplier_window)

    def open_complaint_gui(self) -> None:
        """Open the Complaint Management GUI."""
        self.complaint_window = ComplaintGUI(self)
        self.setCentralWidget(self.complaint_window)

    def back_to_home(self) -> None:
        """Navigate back to the home page."""
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
