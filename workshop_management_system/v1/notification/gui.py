"""Notification GUI Module.

Description:
- This module provides the GUI for managing notifications.

"""

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.notification.model import Notification
from workshop_management_system.v1.notification.view import NotificationView


class NotificationGUI(QMainWindow):
    """Notification GUI Class.

    Description:
    - This class provides the GUI for managing notifications.

    """

    def __init__(self):
        """Initialize the Notification GUI."""
        super().__init__()
        self.setWindowTitle("Notification Management")
        self.setGeometry(100, 100, 800, 600)

        self.notification_view = NotificationView(
            model=Notification
        )  # Initialize NotificationView for CRUD operations

        self.main_layout = QVBoxLayout()

        # Notification table
        self.notification_table = QTableWidget()
        self.notification_table.setSelectionBehavior(
            self.notification_table.SelectionBehavior.SelectRows
        )
        self.main_layout.addWidget(self.notification_table)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Notifications")
        self.load_button.clicked.connect(self.load_notifications)
        button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Notification")
        self.add_button.clicked.connect(self.add_notification)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Notification")
        self.update_button.clicked.connect(self.update_notification)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Notification")
        self.delete_button.clicked.connect(self.delete_notification)
        button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.load_notifications()  # Load notifications on initialization

    def load_notifications(self):
        """Load notifications from the database and display them in the table."""
        try:
            with Session(engine) as session:
                notifications = self.notification_view.read_all(
                    db_session=session
                )
                self.notification_table.setRowCount(len(notifications))
                self.notification_table.setColumnCount(5)
                self.notification_table.setHorizontalHeaderLabels(
                    [
                        "ID",
                        "Customer ID",
                        "Message",
                        "Status",
                        "Notification Date",
                    ]
                )

                for row, notification in enumerate(notifications):
                    self.notification_table.setItem(
                        row, 0, QTableWidgetItem(str(notification.notification_id))
                    )
                    self.notification_table.setItem(
                        row, 1, QTableWidgetItem(str(notification.customer_id))
                    )
                    self.notification_table.setItem(
                        row, 2, QTableWidgetItem(notification.message)
                    )
                    self.notification_table.setItem(
                        row, 3, QTableWidgetItem(notification.status)
                    )
                    self.notification_table.setItem(
                        row,
                        4,
                        QTableWidgetItem(str(notification.notification_date)),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load notifications: {e!s}"
            )

    def add_notification(self):
        """Add a new notification to the database."""
        try:
            # Get notification details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Add Notification", "Enter Customer ID:"
            )
            if not ok:
                return

            message, ok = QInputDialog.getText(
                self, "Add Notification", "Enter Message:"
            )
            if not ok or not message:
                return

            status, ok = QInputDialog.getText(
                self, "Add Notification", "Enter Status:"
            )
            if not ok or not status:
                return

            with Session(engine) as session:
                new_notification = Notification(
                    customer_id=customer_id,
                    message=message,
                    status=status,
                )
                self.notification_view.create(
                    db_session=session, record=new_notification
                )
                QMessageBox.information(
                    self, "Success", "Notification added successfully!"
                )
                self.load_notifications()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add notification: {e!s}"
            )

    def update_notification(self):
        """Update an existing notification."""
        try:
            selected_row = self.notification_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a notification to update."
                )
                return

            item = self.notification_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected notification ID is invalid."
                )
                return
            notification_id = int(item.text())

            # Get updated details from user
            customer_id, ok = QInputDialog.getInt(
                self, "Update Notification", "Enter New Customer ID:"
            )
            if not ok:
                return

            message, ok = QInputDialog.getText(
                self, "Update Notification", "Enter New Message:"
            )
            if not ok or not message:
                return

            status, ok = QInputDialog.getText(
                self, "Update Notification", "Enter New Status:"
            )
            if not ok or not status:
                return

            with Session(engine) as session:
                notification_obj = self.notification_view.read_by_id(
                    db_session=session, record_id=notification_id
                )
                if notification_obj:
                    notification_obj.customer_id = customer_id
                    notification_obj.message = message
                    notification_obj.status = status
                    self.notification_view.update(
                        db_session=session,
                        record_id=notification_id,
                        record=notification_obj,
                    )
                    QMessageBox.information(
                        self, "Success", "Notification updated successfully!"
                    )
                    self.load_notifications()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update notification: {e!s}"
            )

    def delete_notification(self):
        """Delete a notification from the database."""
        try:
            selected_row = self.notification_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(
                    self, "Warning", "Please select a notification to delete."
                )
                return

            item = self.notification_table.item(selected_row, 0)
            if item is None:
                QMessageBox.warning(
                    self, "Warning", "Selected notification ID is invalid."
                )
                return
            notification_id = int(item.text())

            confirmation = QMessageBox.question(
                self,
                "Delete Notification",
                "Are you sure you want to delete this notification?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                with Session(engine) as session:
                    self.notification_view.delete(
                        db_session=session, record_id=notification_id
                    )
                    QMessageBox.information(
                        self, "Success", "Notification deleted successfully!"
                    )
                    self.load_notifications()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to delete notification: {e!s}"
            )


if __name__ == "__main__":
    app = QApplication([])
    window = NotificationGUI()
    window.show()
    app.exec()
