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

from workshop_management_system.v1.customer.gui import CustomerGUI
from workshop_management_system.v1.employee.gui import EmployeeGUI
from workshop_management_system.v1.estimate.gui import EstimateGUI
from workshop_management_system.v1.feedback.gui import FeedBackGUI
from workshop_management_system.v1.vehicle.gui import VehicleGUI


class HomeGUI(QMainWindow):
    """Home GUI Class.

    Description:
    - This class provides the main GUI for navigating the application.

    """

    def __init__(self):
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

        self.customer_button = QPushButton("Manage Customers")
        self.customer_button.setIcon(QIcon("icons/customer.png"))
        self.customer_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #4CAF50; "
            "color: white;"
        )
        self.customer_button.clicked.connect(self.open_customer_gui)
        button_layout.addWidget(self.customer_button, 0, 0)

        self.inventory_button = QPushButton("Manage Inventory")
        self.inventory_button.setIcon(QIcon("icons/inventory.png"))
        self.inventory_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #2196F3; "
            "color: white;"
        )
        self.inventory_button.clicked.connect(self.open_inventory_gui)
        button_layout.addWidget(self.inventory_button, 0, 1)

        self.job_card_button = QPushButton("Manage Job Cards")
        self.job_card_button.setIcon(QIcon("icons/job_card.png"))
        self.job_card_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #FF9800; "
            "color: white;"
        )
        self.job_card_button.clicked.connect(self.open_job_card_gui)
        button_layout.addWidget(self.job_card_button, 1, 0)

        self.employee_button = QPushButton("Manage Employees")
        self.employee_button.setIcon(QIcon("icons/employee.png"))
        self.employee_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #9C27B0; "
            "color: white;"
        )
        self.employee_button.clicked.connect(self.open_employee_gui)
        button_layout.addWidget(self.employee_button, 1, 1)

        self.estimate_button = QPushButton("Manage Estimates")
        self.estimate_button.setIcon(QIcon("icons/estimate.png"))
        self.estimate_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #F44336; "
            "color: white;"
        )
        self.estimate_button.clicked.connect(self.open_estimate_gui)
        button_layout.addWidget(self.estimate_button, 2, 0, 1, 2)

        self.feedback_button = QPushButton("Manage Feedback")
        self.feedback_button.setIcon(QIcon("icons/feedback.png"))
        self.feedback_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #FF5722; "
            "color: white;"
        )
        self.feedback_button.clicked.connect(self.open_feedback_gui)
        button_layout.addWidget(self.feedback_button, 2, 1)

        self.vehicle_button = QPushButton("Manage Vehicles")
        self.vehicle_button.setIcon(QIcon("icons/vehicle.png"))
        self.vehicle_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #607D8B; "
            "color: white;"
        )
        self.vehicle_button.clicked.connect(self.open_vehicle_gui)
        button_layout.addWidget(self.vehicle_button, 3, 0)

        self.main_layout.addWidget(button_frame)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def open_customer_gui(self):
        """Open the Customer Management GUI."""
        self.customer_window = CustomerGUI()
        self.customer_window.show()

    def open_inventory_gui(self):
        """Open the Inventory Management GUI."""
        # Placeholder for opening Inventory GUI
        pass

    def open_job_card_gui(self):
        """Open the Job Card Management GUI."""
        # Placeholder for opening Job Card GUI
        pass

    def open_employee_gui(self):
        """Open the Employee Management GUI."""
        self.employee_window = EmployeeGUI()
        self.employee_window.show()

    def open_estimate_gui(self):
        """Open the Estimate Management GUI."""
        self.estimate_window = EstimateGUI()
        self.estimate_window.show()

    def open_feedback_gui(self):
        """Open the Feedback Management GUI."""
        self.feedback_window = FeedBackGUI()
        self.feedback_window.show()

    def open_vehicle_gui(self):
        """Open the Vehicle Management GUI."""
        self.vehicle_window = VehicleGUI()
        self.vehicle_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = HomeGUI()
    window.show()
    app.exec()
