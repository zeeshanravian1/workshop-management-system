"""Home GUI Module.

Description:
- This module provides the main GUI for navigating different sections of the
  application.

"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
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
        self.setGeometry(100, 100, 600, 400)

        self.main_layout = QVBoxLayout()

        # Welcome message
        self.welcome_label = QLabel(
            "Welcome to the Workshop Management System"
        )
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.welcome_label)

        # Frame for buttons
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.Shape.Box)
        button_frame.setFrameShadow(QFrame.Shadow.Raised)
        button_layout = QGridLayout(button_frame)

        buttons = [
            ("Manage Customers", "icons/customer.png", self.open_customer_gui),
            (
                "Manage Inventory",
                "icons/inventory.png",
                self.open_inventory_gui,
            ),
            ("Manage Job Cards", "icons/job_card.png", self.open_job_card_gui),
            ("Manage Estimates", "icons/estimate.png", self.open_estimate_gui),
            ("Manage Feedback", "icons/feedback.png", self.open_complaint_gui),
            ("Manage Vehicles", "icons/vehicle.png", self.open_vehicle_gui),
            ("Manage Payments", "icons/payment.png", self.open_payment_gui),
            ("Manage Suppliers", "icons/supplier.png", self.open_supplier_gui),
        ]

        row, col = 0, 0
        for text, icon, method in buttons:
            button = QPushButton(text)
            button.setIcon(QIcon(icon))
            button.setStyleSheet(
                "padding: 10px; font-size: 14px; "
                "background-color: #4CAF50; color: white;"
            )
            button.clicked.connect(method)
            button_layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                row += 1
                col = 0

        self.main_layout.addWidget(button_frame)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def open_customer_gui(self) -> None:
        """Open the Customer Management GUI."""
        self.customer_window = CustomerGUI()
        self.customer_window.show()

    def open_inventory_gui(self) -> None:
        """Open the Inventory Management GUI."""
        self.inventory_window = InventoryGUI()
        self.inventory_window.show()

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        self.jobcard_window = JobCardGUI()
        self.jobcard_window.show()

    def open_estimate_gui(self) -> None:
        """Open the Estimate Management GUI."""
        self.estimate_window = EstimateGUI()
        self.estimate_window.show()

    def open_vehicle_gui(self) -> None:
        """Open the Vehicle Management GUI."""
        self.vehicle_window = VehicleGUI()
        self.vehicle_window.show()

    def open_payment_gui(self) -> None:
        """Open the Payment Management GUI."""
        self.payment_window = PaymentGUI()
        self.payment_window.show()

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
