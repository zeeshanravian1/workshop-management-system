import random

from faker import Faker
from sqlmodel import Session

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.supplier.model import Supplier


def generate_sample_suppliers(count: int = 1000) -> None:
    """Generate sample supplier data."""
    fake = Faker()

    try:
        with Session(engine) as session:
            suppliers = []
            for _ in range(count):
                # Generate realistic supplier data
                supplier = Supplier(
                    name=fake.company(),
                    email=fake.company_email(),
                    contact_number=f"+{random.randint(1, 99)}{fake.msisdn()[3:]}",
                    address=fake.address().replace("\n", ", "),
                )
                suppliers.append(supplier)

            # Bulk insert suppliers
            session.add_all(suppliers)
            session.commit()

            print(f"Successfully created {count} sample suppliers")

    except Exception as e:
        print(f"Error generating sample data: {e}")
        session.rollback()  # Rollback on error


if __name__ == "__main__":
    generate_sample_suppliers()
