"""This module contains the view for the estimate module."""

from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)


class EstimateView(QWidget):
    """A widget that displays and manages workshop service estimates."""

    def __init__(self):
        """Initialize the estimate view."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Set up the estimate view UI."""
        layout = QGridLayout()
        self.setLayout(layout)

        # Existing fields
        self.customer_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.service_type = QComboBox()
        self.service_type.addItems(["Repair", "Installation", "Maintenance"])
        self.description = QLineEdit()

        # Tax related fields
        self.base_amount = QDoubleSpinBox()
        self.base_amount.setRange(0, 1000000)
        self.nhil = QLineEdit()
        self.nhil.setReadOnly(True)
        self.getfund = QLineEdit()
        self.getfund.setReadOnly(True)
        self.covid_levy = QLineEdit()
        self.covid_levy.setReadOnly(True)
        self.vat = QLineEdit()
        self.vat.setReadOnly(True)
        self.total = QLineEdit()
        self.total.setReadOnly(True)

        # Layout
        row = 0
        layout.addWidget(QLabel("Customer Name:"), row, 0)
        layout.addWidget(self.customer_name, row, 1)

        row += 1
        layout.addWidget(QLabel("Email:"), row, 0)
        layout.addWidget(self.email, row, 1)

        row += 1
        layout.addWidget(QLabel("Base Amount:"), row, 0)
        layout.addWidget(self.base_amount, row, 1)

        row += 1
        layout.addWidget(QLabel("NHIL (2.5%):"), row, 0)
        layout.addWidget(self.nhil, row, 1)

        row += 1
        layout.addWidget(QLabel("GETFUND (2.5%):"), row, 0)
        layout.addWidget(self.getfund, row, 1)

        row += 1
        layout.addWidget(QLabel("COVID Levy (1%):"), row, 0)
        layout.addWidget(self.covid_levy, row, 1)

        row += 1
        layout.addWidget(QLabel("VAT (15%):"), row, 0)
        layout.addWidget(self.vat, row, 1)

        row += 1
        layout.addWidget(QLabel("Total (inc. Tax):"), row, 0)
        layout.addWidget(self.total, row, 1)

        # Add buttons
        self.save_button = QPushButton("Save")
        self.clear_button = QPushButton("Clear")
        layout.addWidget(self.save_button, row + 1, 0)
        layout.addWidget(self.clear_button, row + 1, 1)

        # Connect signals
        self.base_amount.valueChanged.connect(self.calculate_taxes)
        self.clear_button.clicked.connect(self.clear_fields)

    def clear_fields(self):
        """Clear all input fields."""
        self.customer_name.clear()
        self.email.clear()
        self.phone.clear()
        self.service_type.setCurrentIndex(0)
        self.description.clear()
        self.base_amount.setValue(0)
        self.nhil.clear()
        self.getfund.clear()
        self.covid_levy.clear()
        self.vat.clear()
        self.total.clear()

    def show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)

    def show_success(self, message):
        """Show a success message."""
        QMessageBox.information(self, "Success", message)

    def calculate_taxes(self):
        """Calculate taxes based on the base amount."""
        base = self.base_amount.value()
        nhil = base * 0.025
        getfund = base * 0.025
        covid = base * 0.01
        subtotal = base + nhil + getfund + covid
        vat = subtotal * 0.15
        total = subtotal + vat

        self.nhil.setText(f"{nhil:.2f}")
        self.getfund.setText(f"{getfund:.2f}")
        self.covid_levy.setText(f"{covid:.2f}")
        self.vat.setText(f"{vat:.2f}")
        self.total.setText(f"{total:.2f}")
