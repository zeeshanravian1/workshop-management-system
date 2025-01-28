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
from workshop_management_system.v1.service.gui import ServiceGUI
from workshop_management_system.v1.service_item.gui import ServiceItemGUI
from workshop_management_system.v1.stock_transaction.gui import (
    StockTransactionGUI,
)
from workshop_management_system.v1.supplier.gui import SupplierGUI


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

        self.customer_button = QPushButton("Manage Customers")
        self.customer_button.clicked.connect(self.open_customer_gui)
        self.main_layout.addWidget(self.customer_button)

        self.service_button = QPushButton("Manage Services")
        self.service_button.clicked.connect(self.open_service_gui)
        self.main_layout.addWidget(self.service_button)

        self.inventory_button = QPushButton("Manage Inventory")
        self.inventory_button.clicked.connect(self.open_inventory_gui)
        self.main_layout.addWidget(self.inventory_button)

        self.job_card_button = QPushButton("Manage Job Cards")
        self.job_card_button.clicked.connect(self.open_job_card_gui)
        self.main_layout.addWidget(self.job_card_button)

        self.service_item_button = QPushButton("Manage Service Items")
        self.service_item_button.clicked.connect(self.open_service_item_gui)
        self.main_layout.addWidget(self.service_item_button)

        self.stock_transaction_button = QPushButton(
            "Manage Stock Transactions"
        )
        self.stock_transaction_button.clicked.connect(
            self.open_stock_transaction_gui
        )
        self.main_layout.addWidget(self.stock_transaction_button)

        self.supplier_button = QPushButton("Manage Suppliers")
        self.supplier_button.clicked.connect(self.open_supplier_gui)
        self.main_layout.addWidget(self.supplier_button)

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
        # Placeholder for opening Inventory GUI
        pass

    def open_job_card_gui(self) -> None:
        """Open the Job Card Management GUI."""
        # Placeholder for opening Job Card GUI
        pass

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
