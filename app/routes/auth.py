from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        company_name = request.form.get('companyName')
        phone_number = request.form.get('phoneNumber')
        password = request.form.get('password')

        if not full_name or not email or not company_name or not phone_number or not password:
            flash("All fields are required", "danger")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "danger")
            return redirect(url_for('auth.register'))

        user = User(
            full_name=full_name,
            company_name=company_name,
            phone_number=phone_number,
            email=email
        )
        user.set_password(password)
        user.is_admin = True
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_after_login(current_user)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect_after_login(user)
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

def redirect_after_login(user):
    if user.role == User.ROLE_ADMIN:

        return redirect(url_for('dashboard.index'))  # or your admin page
    else:
        return redirect(url_for('timesheets.self_timesheets'))  # or user dashboard

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('auth.login'))



