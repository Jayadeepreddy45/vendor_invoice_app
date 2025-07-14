from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Vendor, Timesheet, Invoice, InvoiceItem, User
from datetime import datetime
from collections import defaultdict
from flask import jsonify

bp = Blueprint('invoices', __name__, url_prefix='/invoice')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('invoice_form.html')



@bp.route('/invoices/manage')
@login_required
def invoice_management():
    return render_template('invoice_management.html')

@bp.route('/list', methods=['GET'])
@login_required
def list_invoices():
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    invoices = (
        db.session.query(Invoice, Vendor)
        .join(Vendor, Invoice.vendor_id == Vendor.id)
        .order_by(Invoice.id.desc())
        .all()
    )

    return jsonify([
        {
            "id": inv.id,
            "number": inv.invoice_number,
            "vendor": ven.name,
            "vendor_email": ven.email,
            "status": inv.status,
            "due_date": inv.due_date.strftime('%Y-%m-%d') if inv.due_date else '',
            "total": f"${inv.total_amount:,.2f}"
        }
        for inv, ven in invoices
    ])


@bp.route('/vendors', methods=['GET'])
@login_required
def get_vendors():
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    vendors = Vendor.query.order_by(Vendor.name).all()
    return jsonify([
        {"id": v.id, "name": v.name} for v in vendors
    ])


@bp.route('/api/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice_data(invoice_id):
    # Only admins should access invoice details
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    invoice = Invoice.query.get_or_404(invoice_id)
    items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()

    data = {
        "invoice_number": invoice.invoice_number,
        "items": []
    }

    for item in items:
        employee = User.query.get(item.employee_id)
        data["items"].append({
            "id": item.id,
            "employee_name": employee.username,  # or full_name if available
            "hours": item.hours,
            "rate": item.rate
        })

    return jsonify(data)


@bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(invoice_id):
    # Only admins may edit
    if current_user.role != User.ROLE_ADMIN:
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard.index'))

    invoice = Invoice.query.get_or_404(invoice_id)
    items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()

    if request.method == 'POST':
        action = request.form.get('action')

        # Update line-item values from form
        total = 0.0
        for item in items:
            hours_key = f"hours_{item.id}"
            rate_key  = f"rate_{item.id}"
            try:
                new_hours = float(request.form.get(hours_key, item.hours))
                new_rate  = float(request.form.get(rate_key, item.rate))
            except ValueError:
                continue  # skip invalid inputs

            item.hours    = new_hours
            item.rate     = new_rate
            item.subtotal = new_hours * new_rate
            total        += item.subtotal

        invoice.total_amount = total

        if action == 'finalize':
            invoice.status = 'Finalized'
            flash("Invoice finalized.", "success")
        else:
            flash("Recalculated invoice totals.", "info")

        db.session.commit()
        # refresh items for GET
        return redirect(url_for('invoices.edit', invoice_id=invoice.id))

    # GET: render form
    return render_template('invoices/edit.html', invoice=invoice)

