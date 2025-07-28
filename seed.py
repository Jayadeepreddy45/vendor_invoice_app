from app import app, db
from app.models import User, Vendor, EmployeeVendor, Timesheet
from datetime import date

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create Admin
    admin = User(full_name="Admin User", company_name="Admin Inc", email="admin@example.com",
                 phone_number="1234567890", role=User.ROLE_ADMIN)
    admin.set_password("adminpass")

    # Create Employees
    emp1 = User(full_name="Alice Doe", company_name="Emp1 Corp", email="alice@example.com",
                phone_number="9876543210", role=User.ROLE_USER)
    emp1.set_password("password")

    emp2 = User(full_name="Bob Smith", company_name="Emp2 Corp", email="bob@example.com",
                phone_number="5555555555", role=User.ROLE_USER)
    emp2.set_password("password")

    # Create Vendors
    v1 = Vendor(name="Vendor A", email="vendorA@example.com", phone="1112223333", address="123 Vendor Lane", terms="30")
    v2 = Vendor(name="Vendor B", email="vendorB@example.com", phone="4445556666", address="456 Vendor Road", terms="45")

    db.session.add_all([admin, emp1, emp2, v1, v2])
    db.session.commit()

    # Map Employee to Vendors with different rates
    ev1 = EmployeeVendor(employee_id=emp1.id, vendor_id=v1.id, hourly_rate=30.0)
    ev2 = EmployeeVendor(employee_id=emp1.id, vendor_id=v2.id, hourly_rate=35.0)
    ev3 = EmployeeVendor(employee_id=emp2.id, vendor_id=v1.id, hourly_rate=28.0)

    db.session.add_all([ev1, ev2, ev3])
    db.session.commit()

    # Add Timesheets
    t1 = Timesheet(employee_id=emp1.id, vendor_id=v1.id, date=date(2025, 7, 15), hours=6, project_description="UI work")
    t2 = Timesheet(employee_id=emp1.id, vendor_id=v2.id, date=date(2025, 7, 16), hours=7, project_description="Backend refactor")
    t3 = Timesheet(employee_id=emp2.id, vendor_id=v1.id, date=date(2025, 7, 17), hours=5, project_description="Testing")

    db.session.add_all([t1, t2, t3])
    db.session.commit()

    print("✅ Sample data inserted successfully!")
