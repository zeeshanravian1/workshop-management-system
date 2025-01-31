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
from workshop_management_system.v1.inventory.gui import InventoryGUI
from workshop_management_system.v1.jobcard.gui import JobCardGUI
from workshop_management_system.v1.notification.gui import NotificationGUI
from workshop_management_system.v1.payment.gui import PaymentGUI
from workshop_management_system.v1.service.gui import ServiceGUI
from workshop_management_system.v1.service_item.gui import ServiceItemGUI
from workshop_management_system.v1.stock_transaction.gui import (
    StockTransactionGUI,
)
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
            ("Manage Services", "icons/service.png", self.open_service_gui),
            (
                "Manage Inventory",
                "icons/inventory.png",
                self.open_inventory_gui,
            ),
            ("Manage Job Cards", "icons/job_card.png", self.open_job_card_gui),
            ("Manage Employees", "icons/employee.png", self.open_employee_gui),
            ("Manage Estimates", "icons/estimate.png", self.open_estimate_gui),
            ("Manage Feedback", "icons/feedback.png", self.open_feedback_gui),
            ("Manage Vehicles", "icons/vehicle.png", self.open_vehicle_gui),
            ("Manage Payments", "icons/payment.png", self.open_payment_gui),
            (
                "Manage Notifications",
                "icons/notification.png",
                self.open_notification_gui,
            ),
            (
                "Manage Service Items",
                "icons/serviceitem.png",
                self.open_service_item_gui,
            ),
            (
                "Manage Stock Transactions",
                "icons/stocktransaction.png",
                self.open_stock_transaction_gui,
            ),
            ("Manage Suppliers", "icons/supplier.png", self.open_supplier_gui),
        ]

        row, col = 0, 0
        for text, icon, method in buttons:
            button = QPushButton(text)
            button.setIcon(QIcon(icon))
            button.setStyleSheet(
                "padding: 10px; font-size: 14px; background-color: #4CAF50; color: white;"
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

    def open_service_gui(self) -> None:
        """Open the Service Management GUI."""
        self.service_window = ServiceGUI()
        self.service_window.show()

    def open_inventory_gui(self) -> None:
        """Open the Inventory Management GUI."""
        self.inventory_window = InventoryGUI()
        self.inventory_window.show()

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        self.jobcard_window = JobCardGUI()
        self.jobcard_window.show()

    def open_employee_gui(self) -> None:
        """Open the Employee Management GUI."""
        self.employee_window = EmployeeGUI()
        self.employee_window.show()

    def open_estimate_gui(self) -> None:
        """Open the Estimate Management GUI."""
        self.estimate_window = EstimateGUI()
        self.estimate_window.show()

    def open_feedback_gui(self) -> None:
        """Open the Feedback Management GUI."""
        self.feedback_window = FeedBackGUI()
        self.feedback_window.show()

    def open_vehicle_gui(self) -> None:
        """Open the Vehicle Management GUI."""
        self.vehicle_window = VehicleGUI()
        self.vehicle_window.show()

    def open_payment_gui(self) -> None:
        """Open the Payment Management GUI."""
        self.payment_window = PaymentGUI()
        self.payment_window.show()

    def open_notification_gui(self) -> None:
        """Open the Notification Management GUI."""
        self.notification_window = NotificationGUI()
        self.notification_window.show()

    def open_service_item_gui(self) -> None:
        """Open the Service Item Management GUI."""
        self.service_item_window = ServiceItemGUI()
        self.service_item_window.show()

    def open_stock_transaction_gui(self) -> None:
        """Open the Stock Transaction Management GUI."""
        self.stock_transaction_window = StockTransactionGUI()
        self.stock_transaction_window.show()

    def open_supplier_gui(self) -> None:
        """Open the Supplier Management GUI."""
        self.supplier_window = SupplierGUI()
        self.supplier_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = HomeGUI()
    window.show()
    app.exec()
