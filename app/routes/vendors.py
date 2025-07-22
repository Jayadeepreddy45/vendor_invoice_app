# Vendor routes
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Vendor
from app.models import User


bp = Blueprint('vendors', __name__)
@bp.route('/vendor/create', methods=['GET', 'POST'])
@login_required
def create_vendor():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        invoice_prefix = request.form.get('invoice_prefix')

        if not name:
            flash('Vendor name is required.', 'danger')
            return redirect(url_for('vendors.create_vendor'))

        vendor = Vendor(name=name, address=address, phone=phone,email=email, terms=invoice_prefix)
        db.session.add(vendor)
        db.session.commit()

        flash('Vendor created successfully.', 'success')
        return redirect(url_for('vendors.list_vendors'))

    return render_template('vendor_form.html')

@bp.route('/vendor/list')
@login_required
def list_vendors():
    if current_user.role != User.ROLE_ADMIN:
        flash("Access denied", "danger")
        return redirect(url_for('dashboard.index'))

    vendors = Vendor.query.order_by(Vendor.name).all()
    return render_template('vendor_list.html', vendors=vendors)

@bp.route('/api/vendors')
@login_required
def api_vendors():
    from app.models import Vendor

    vendors = Vendor.query.order_by(Vendor.name).all()
    return jsonify([
        {
            "id": v.id,
            "name": v.name
        }
        for v in vendors
    ])

@bp.route('/vendor/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_vendor(id):
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    return jsonify({"message": "Vendor deleted"})

@bp.route('/vendor/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)

    if request.method == 'POST':
        vendor.name = request.form.get('name')
        vendor.email = request.form.get('email')
        vendor.phone = request.form.get('phone')
        vendor.address = request.form.get('address')
        vendor.terms = request.form.get('terms')

        db.session.commit()
        flash("Vendor updated successfully", "success")
        return redirect(url_for('vendors.list_vendors'))

    return render_template('vendor_form.html', vendor=vendor)