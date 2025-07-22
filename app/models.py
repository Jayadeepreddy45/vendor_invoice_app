# Models will be defined here
from . import db
from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# 🧑‍💻 User
class User(UserMixin, db.Model):
    ROLE_USER = 1
    ROLE_ADMIN = 2

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Integer, default=ROLE_USER)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20)) 
    terms = db.Column(db.String(200))
    address = db.Column(db.String(200))
    employees = db.relationship('Employee', backref='vendor', lazy=True)
    invoices = db.relationship('Invoice', backref='vendor', lazy=True)


# 👨‍🏭 Employee
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    invoice_items = db.relationship('InvoiceItem', backref='employee', lazy=True)

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    project_description = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')

    employee = db.relationship('User', backref='timesheets')




# 📄 Invoice
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

# 🧾 InvoiceItem
class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

# 💳 Payment
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_on = db.Column(db.Date, default=datetime.utcnow)
