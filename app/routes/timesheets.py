from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Timesheet, User

bp = Blueprint('timesheets', __name__)

# ---------------------------
# SELF Timesheet Submission
# ---------------------------
@bp.route('/timesheets/self', methods=['GET', 'POST'])
@login_required
def self_timesheets():
    if current_user.role != 1:
        flash("Access denied", "danger")
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json()
        print("Payload:", data)

        date_str = data.get('date')
        hours = data.get('hours')
        project_description = data.get('project_description', '')

        if not date_str or not hours:
            return jsonify({"error": "Date and hours are required."}), 400

        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            hours = float(hours)
        except ValueError as e:
            print("Parse error:", e)
            return jsonify({"error": "Invalid input format"}), 400

        timesheet = Timesheet(
            employee_id=current_user.id,
            date=entry_date,
            hours=hours,
            project_description=project_description
        )
        db.session.add(timesheet)
        db.session.commit()
        print("✅ Timesheet saved")

        return jsonify({"message": "Success"}), 200

    # GET: Show only current user's timesheets
    timesheets = Timesheet.query.filter_by(employee_id=current_user.id).order_by(Timesheet.date.desc()).all()
    return render_template("timesheets_self.html", timesheets=timesheets)


# ---------------------------
# Admin: View All Timesheets
# ---------------------------
@bp.route('/timesheets/all')
@login_required
def view_all_timesheets():
    if current_user.role != User.ROLE_ADMIN:
        flash("Access denied", "danger")
        return redirect(url_for('dashboard.index'))

    all_timesheets = Timesheet.query.join(User).order_by(Timesheet.date.desc()).all()
    return render_template('admin_timesheets.html', timesheets=all_timesheets)


# ---------------------------
# Approve Timesheet
# ---------------------------
@bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve(id):
    if current_user.role != User.ROLE_ADMIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))

    timesheet = Timesheet.query.get_or_404(id)
    timesheet.status = 'Approved'
    db.session.commit()
    flash("Timesheet approved", "success")
    return redirect(url_for('timesheets.view_all_timesheets'))


# ---------------------------
# Reject Timesheet
# ---------------------------
@bp.route('/reject/<int:id>', methods=['POST'])
@login_required
def reject(id):
    if current_user.role != User.ROLE_ADMIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))

    timesheet = Timesheet.query.get_or_404(id)
    timesheet.status = 'Rejected'
    db.session.commit()
    flash("Timesheet rejected", "warning")
    return redirect(url_for('timesheets.view_all_timesheets'))


# ---------------------------
# API: All Timesheets JSON
# ---------------------------
@bp.route('/api/timesheets')
@login_required
def api_all_timesheets():
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    timesheets = Timesheet.query.join(User).order_by(Timesheet.date.desc()).all()
    return jsonify([
        {
            "id": t.id,
            "employee_name": t.employee.full_name,
            "date": t.date.strftime('%Y-%m-%d'),
            "hours": t.hours,
            "project_description": t.project_description,
            "status": t.status
        }
        for t in timesheets
    ])


# ---------------------------
# API: Update Timesheet Status
# ---------------------------
@bp.route('/api/timesheets/<int:id>/status', methods=['POST'])
@login_required
def update_timesheet_status(id):
    if current_user.role != User.ROLE_ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    status = data.get("status")

    if status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    timesheet = Timesheet.query.get_or_404(id)
    timesheet.status = status
    db.session.commit()
    return jsonify({"message": "Status updated"})
