"""Main module for project.

Description:
- This module is main file for project.

"""

from pydantic_extra_types.phone_numbers import PhoneNumber

from workshop_management_system.core.load_models import load_all_models
from workshop_management_system.database.session import get_session
from workshop_management_system.v1.customer.model import Customer, CustomerBase
from workshop_management_system.v1.customer.view import CustomerView

load_all_models()

SEPERATOR: str = "************************************************************"

# Instantiate views
customer_view = CustomerView(Customer)


with get_session() as session:
    print("Creating Customers...")

    for i in range(1, 10001):
        contact_number = PhoneNumber(f"+92300{10000 + i}67")

        customer = CustomerBase(
            name=f"John Doe {i}",
            email=f"john.doe{i}@example.com",
            contact_no=contact_number,
            address=f"{i} Main Street, Springfield",
        )

        new_customer: Customer = customer_view.create(
            db_session=session, record=Customer(**customer.model_dump())
        )
        print(f"Customer Created: {new_customer.model_dump()}")
        print(SEPERATOR)
