"""Sample data for supplier testing."""

from sqlmodel import Session, SQLModel

from workshop_management_system.database.connection import engine
from workshop_management_system.v1.supplier.model import Supplier


def create_tables():
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def add_sample_suppliers():
    """Add sample suppliers to the database."""
    try:
        # First create tables
        create_tables()

        with Session(engine) as session:
            # Check if suppliers already exist
            existing = session.query(Supplier).first()
            if existing:
                print("Suppliers already exist in database!")
                return

            for supplier_data in sample_suppliers:
                supplier = Supplier(**supplier_data)
                session.add(supplier)
            session.commit()
            print("Sample suppliers added successfully!")
    except Exception as e:
        print(f"Error adding sample suppliers: {e}")


# Sample data
sample_suppliers = [
    {
        "name": "Auto Parts Plus",
        "email": "info@autopartsplus.com",
        "contact_number": "+923001234567",
        "address": "123 Main Street, Karachi",
    },
    {
        "name": "Tech Auto Solutions",
        "email": "sales@techauto.com",
        "contact_number": "+923011234568",
        "address": "456 Market Road, Lahore",
    },
    {
        "name": "Premium Car Parts",
        "email": "contact@premiumparts.com",
        "contact_number": "+923021234569",
        "address": "789 Shop Avenue, Islamabad",
    },
    {
        "name": "Global Auto Traders",
        "email": "info@globalauto.com",
        "contact_number": "+923031234570",
        "address": "321 Trade Center, Rawalpindi",
    },
    {
        "name": "Fast Track Spares",
        "email": "support@fasttrack.com",
        "contact_number": "+923041234571",
        "address": "654 Speed Road, Faisalabad",
    },
    {
        "name": "Elite Motors Supply",
        "email": "elite@motors.com",
        "contact_number": "+923051234572",
        "address": "987 Elite Street, Multan",
    },
    {
        "name": "Star Auto Parts",
        "email": "star@autoparts.com",
        "contact_number": "+923061234573",
        "address": "147 Star Road, Peshawar",
    },
    {
        "name": "Quality Parts Co",
        "email": "info@qualityparts.com",
        "contact_number": "+923071234574",
        "address": "258 Quality Ave, Quetta",
    },
    {
        "name": "Swift Suppliers",
        "email": "swift@suppliers.com",
        "contact_number": "+923081234575",
        "address": "369 Swift Street, Hyderabad",
    },
    {
        "name": "Reliable Auto Store",
        "email": "info@reliable.com",
        "contact_number": "+923091234576",
        "address": "741 Trust Road, Sialkot",
    },
    {
        "name": "Modern Auto Parts",
        "email": "modern@autoparts.com",
        "contact_number": "+923101234577",
        "address": "852 Modern Plaza, Gujranwala",
    },
    {
        "name": "Supreme Spares",
        "email": "supreme@spares.com",
        "contact_number": "+923111234578",
        "address": "963 Supreme Center, Bahawalpur",
    },
    {
        "name": "Quick Auto Supply",
        "email": "quick@autosupply.com",
        "contact_number": "+923121234579",
        "address": "159 Quick Road, Sukkur",
    },
    {
        "name": "Pro Parts Trading",
        "email": "pro@partstrading.com",
        "contact_number": "+923131234580",
        "address": "753 Pro Street, Abbottabad",
    },
    {
        "name": "Master Auto Components",
        "email": "master@components.com",
        "contact_number": "+923141234581",
        "address": "951 Master Road, Sargodha",
    },
]

if __name__ == "__main__":
    add_sample_suppliers()
