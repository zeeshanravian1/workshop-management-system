"""Sample data generator for testing CustomerGUI."""

import sys

from faker import Faker
from PyQt6.QtWidgets import QApplication
from sqlmodel import select

from workshop_management_system.database.session import get_session
from workshop_management_system.v1.customer.gui import CustomerGUI
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView


def generate_sample_customers(num_records=1000):
    """Generate sample customer data."""
    fake = Faker()
    customers = []

    print(f"Generating {num_records} sample customers...")
    for i in range(num_records):
        try:
            customer = Customer(
                name=fake.name(),
                mobile_number=f"+{fake.random_int(min=1, max=99)}-{fake.msisdn()[3:12]}",
                email=fake.email(),
                address=fake.address().replace("\n", ", "),
                is_deleted=False,
            )
            customers.append(customer)
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1} customers...")
        except Exception as e:
            print(f"Error generating customer: {e}")
            continue

    return customers


def setup_database():
    """Set up database with sample data."""
    try:
        customer_view = CustomerView(Customer)

        with get_session() as session:
            # Clear existing data using SQLModel's session.exec()
            print("\nClearing existing customer data...")
            statement = select(Customer)
            results = session.exec(statement).all()
            for result in results:
                session.delete(result)
            session.commit()

            # Generate and add new sample data
            customers = generate_sample_customers(1000)
            print("\nAdding customers to database...")
            count = 0
            for customer in customers:
                try:
                    customer_view.create(db_session=session, record=customer)
                    count += 1
                    if count % 100 == 0:
                        print(f"Added {count} customers...")
                except Exception as e:
                    print(f"Error adding customer: {e}")
                    continue

            print("\nDatabase setup complete!")
            print(f"Total customers added: {count}")

    except Exception as e:
        print(f"Database setup error: {e}")
        sys.exit(1)


def main():
    """Run the customer GUI with sample data."""
    # First set up the database with sample data
    setup_database()

    # Then launch the GUI
    app = QApplication(sys.argv)
    window = CustomerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
