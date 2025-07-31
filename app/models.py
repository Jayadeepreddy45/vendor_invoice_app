from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    ROLE_EMPLOYEE = 1
    ROLE_ADMIN = 2

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Integer, default=ROLE_EMPLOYEE)

    # 👇 New Fields for employee info
    hourly_rate = db.Column(db.Float, nullable=True)

    # 👇 Relationships
    timesheets = db.relationship('Timesheet', backref='user', lazy=True)
    vendor_links = db.relationship('EmployeeVendor', backref='employee', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 🏢 Vendor model
class Vendor(db.Model):
    __tablename__ = 'vendor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    terms = db.Column(db.String(200))
    address = db.Column(db.String(200))

    invoices = db.relationship('Invoice', backref='vendor', lazy=True)
    employee_links = db.relationship('EmployeeVendor', backref='vendor', lazy=True)

class EmployeeVendor(db.Model):
    __tablename__ = 'employee_vendor'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id', ondelete='CASCADE'), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)

    __table_args__ = (db.UniqueConstraint('employee_id', 'vendor_id', name='uq_employee_vendor_combo'),)

# Timesheet (already pointing to users.id — good!)
class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    project_description = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')


# 🧾 Invoice
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Draft")  # Draft, Sent, Paid
    due_date = db.Column(db.Date)
    sent_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)

    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)
    payments = db.relationship('Payment', backref='invoice', lazy=True)

# InvoiceItem — update FK from employee.id → users.id
class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    employee = db.relationship('User')


# 💳 Payments
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_on = db.Column(db.Date, default=datetime.utcnow)
