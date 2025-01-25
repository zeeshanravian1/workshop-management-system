"""Main module for project.

Description:
- This module is main file for project.

"""

from collections.abc import Sequence
from uuid import UUID

from workshop_management_system.database.session import get_session
from workshop_management_system.v1.customer.model import Customer
from workshop_management_system.v1.customer.view import CustomerView
from workshop_management_system.v1.vehicle.model import Vehicle
from workshop_management_system.v1.vehicle.view import VehicleView

# Instantiate views
customer_view = CustomerView(Customer)
vehicle_view = VehicleView(Vehicle)

with get_session() as session:
    print("Creating Customers...")
    # Create a customer
    new_customer1: Customer = customer_view.create(
        db_session=session,
        record=Customer(
            name="John Doe",
            mobile_number="1234567890",
            vehicle_registration_number="ABC123",
            email="john.doe@example.com",
            address="123 Main Street, Springfield",
        ),
    )
    print(f"Customer Created: {new_customer1.model_dump()}")

    # Create another customer
    new_customer2: Customer = customer_view.create(
        db_session=session,
        record=Customer(
            name="Jane Doe",
            mobile_number="0987654321",
            vehicle_registration_number="XYZ789",
            email="jane.doe@example.com",
            address="456 Elm Street, Springfield",
        ),
    )
    print(f"Customer Created: {new_customer2.model_dump()}")

    print("******************************************************************")

    print("Get Single Customer...")
    # Read single customer
    customer: Customer | None = customer_view.read_by_id(
        db_session=session, record_id=new_customer1.id
    )

    if customer:
        print(f"Customer: {customer.model_dump()}")
    else:
        print("Customer not found.")

    print("******************************************************************")

    print("Get Non Existent Customer...")
    # Read non-existent customer
    non_existent_customer: Customer | None = customer_view.read_by_id(
        db_session=session,
        record_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    if non_existent_customer:
        print(f"Customer: {non_existent_customer.model_dump()}")
    else:
        print("Customer not found.")

    print("******************************************************************")

    print("Get All Customers...")
    # Read all customers
    customers: Sequence[Customer] = customer_view.read_all(db_session=session)

    for customer in customers:
        print(f"Customer: {customer.model_dump()}")

    print("******************************************************************")

    print("Updating Customer...")
    # Update a customer
    updated_customer: Customer | None = customer_view.update(
        db_session=session,
        record_id=new_customer1.id,
        record=Customer(
            name="John Smith",
            mobile_number="1234567890",
            vehicle_registration_number="ABC123",
            email="john.smith@example.com",
            address="123 Main Street, Springfield",
        ),
    )

    if updated_customer:
        print(f"Customer Updated: {updated_customer.model_dump()}")
    else:
        print("Customer not found.")

    print("******************************************************************")

    print("Updating Non Existent Customer...")
    # Update a non-existent customer
    updated_non_existent_customer: Customer | None = customer_view.update(
        db_session=session,
        record_id=UUID("00000000-0000-0000-0000-000000000000"),
        record=Customer(
            name="John Smith",
            mobile_number="1234567890",
            vehicle_registration_number="ABC123",
            email="john.smith@example.com",
            address="123 Main Street, Springfield",
        ),
    )

    if updated_non_existent_customer:
        print(
            f"Customer Updated: {updated_non_existent_customer.model_dump()}"
        )
    else:
        print("Customer not found.")

    print("******************************************************************")

    print("Deleting Customer...")
    # Delete a customer
    deleted_customer: Customer | None = customer_view.delete(
        db_session=session, record_id=new_customer2.id
    )

    if deleted_customer:
        print(f"Customer Deleted: {deleted_customer.model_dump()}")
    else:
        print("Customer not found.")

    print("******************************************************************")

    print("Deleting Non Existent Customer...")
    # Delete a non-existent customer
    deleted_non_existent_customer: Customer | None = customer_view.delete(
        db_session=session,
        record_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    if deleted_non_existent_customer:
        print(
            f"Customer Deleted: {deleted_non_existent_customer.model_dump()}"
        )
    else:
        print("Customer not found.")

    print("******************************************************************")
