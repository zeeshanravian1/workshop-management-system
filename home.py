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
            }
            QLabel {
                color: #333;
            }
        """)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        welcome_label = QLabel("Workshop Management System")
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(welcome_label)
        main_layout.addLayout(header_layout)

        # Description
        description_label = QLabel(
            "Manage your workshop operations efficiently"
        )
        description_label.setFont(QFont("Arial", 12))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description_label)

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

        main_layout.addWidget(button_frame)

    def open_customer_gui(self) -> None:
        """Open the Customer Management GUI."""
        self.customer_window = CustomerGUI()
        self.customer_window.show()

    def open_vehicle_gui(self) -> None:
        """Open the Vehicle Management GUI."""
        self.vehicle_window = VehicleGUI()
        self.vehicle_window.show()

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        self.jobcard_window = JobCardGUI()
        self.jobcard_window.show()

    def open_estimate_gui(self) -> None:
        """Open the Estimate Management GUI."""
        self.estimate_window = EstimateGUI()
        self.estimate_window.show()

    def open_payment_gui(self) -> None:
        """Open the Payment Management GUI."""
        self.payment_window = PaymentGUI()
        self.payment_window.show()

    def open_inventory_gui(self) -> None:
        """Open the Inventory Management GUI."""
        self.inventory_window = InventoryGUI()
        self.inventory_window.show()

    def open_supplier_gui(self) -> None:
        """Open the Supplier Management GUI."""
        self.supplier_window = SupplierGUI()
        self.supplier_window.show()

    def open_complaint_gui(self) -> None:
        """Open the Complaint Management GUI."""
        self.complaint_window = ComplaintGUI()
        self.complaint_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = HomeGUI()
    window.show()
    app.exec()
