"""Home GUI Module.

Description:
- This module provides the main GUI for navigating different sections of the
  application.

"""

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from workshop_management_system.v1.customer.gui import CustomerGUI
from workshop_management_system.v1.inventory.gui import InventoryGUI
from workshop_management_system.v1.jobcard.gui import JobCardGUI
from workshop_management_system.v1.notification.gui import NotificationGUI
from workshop_management_system.v1.payment.gui import PaymentGUI


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

        self.customer_button = QPushButton("Manage Customers")
        self.customer_button.clicked.connect(self.open_customer_gui)
        self.main_layout.addWidget(self.customer_button)

        self.inventory_button = QPushButton("Manage Inventory")
        self.inventory_button.clicked.connect(self.open_inventory_gui)
        self.main_layout.addWidget(self.inventory_button)

        self.job_card_button = QPushButton("Manage Job Cards")
        self.job_card_button.clicked.connect(self.open_job_card_gui)
        self.main_layout.addWidget(self.job_card_button)

        self.payment_button = QPushButton("Manage Payments")
        self.payment_button.clicked.connect(self.open_payment_gui)
        self.main_layout.addWidget(self.payment_button)

        self.notification_button = QPushButton("Manage Notifications")
        self.notification_button.clicked.connect(self.open_notification_gui)
        self.main_layout.addWidget(self.notification_button)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def open_customer_gui(self):
        """Open the Customer Management GUI."""
        self.customer_window = CustomerGUI()
        self.customer_window.show()

    def open_inventory_gui(self):
        """Open the Inventory Management GUI."""
        self.inventory_window = InventoryGUI()
        self.inventory_window.show()

    def open_job_card_gui(self):
        """Open the Job Card Management GUI."""
        self.jobcard_window = JobCardGUI()
        self.jobcard_window.show()

    def open_payment_gui(self):
        """Open the Payment Management GUI."""
        self.payment_window = PaymentGUI()
        self.payment_window.show()

    def open_notification_gui(self):
        """Open the Notification Management GUI."""
        self.notification_window = NotificationGUI()
        self.notification_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = HomeGUI()
    window.show()
    app.exec()
