from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Machine, PreventiveSchedule
from app.utils.decorators import role_required

schedules_bp = Blueprint('schedules', __name__, url_prefix='/machine')

# Frequency to days mapping for auto-calculating next_due
FREQUENCY_DAYS = {
    'daily': 1,
    'weekly': 7,
    'monthly': 30,
    'quarterly': 90,
    'yearly': 365,
}


@schedules_bp.route('/<machine_id>/schedule/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def add_schedule(machine_id):
    """Add a preventive maintenance schedule for a machine."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()

    if request.method == 'POST':
        schedule = PreventiveSchedule(
            machine_id=machine.id,
            task_description=request.form.get('task_description', '').strip(),
            frequency=request.form.get('frequency', 'monthly'),
            assigned_to=request.form.get('assigned_to', '').strip(),
            is_active=True
        )

        # Parse next_due date
        next_due_str = request.form.get('next_due', '').strip()
        if next_due_str:
            try:
                schedule.next_due = datetime.strptime(next_due_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid next due date format.', 'error')
                return render_template('schedules/add.html', machine=machine)
        else:
            flash('Next due date is required.', 'error')
            return render_template('schedules/add.html', machine=machine)

        if not schedule.task_description:
            flash('Task description is required.', 'error')
            return render_template('schedules/add.html', machine=machine)

        try:
            db.session.add(schedule)
            db.session.commit()
            flash('Preventive schedule added successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding schedule: {str(e)}', 'error')

    return render_template('schedules/add.html', machine=machine)


@schedules_bp.route('/<machine_id>/schedule/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def edit_schedule(machine_id, id):
    """Edit a preventive maintenance schedule."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    schedule = PreventiveSchedule.query.get_or_404(id)

    if schedule.machine_id != machine.id:
        flash('Schedule not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    if request.method == 'POST':
        schedule.task_description = request.form.get('task_description', schedule.task_description).strip()
        schedule.frequency = request.form.get('frequency', schedule.frequency)
        schedule.assigned_to = request.form.get('assigned_to', '').strip()
        schedule.is_active = request.form.get('is_active') == 'on'

        # Parse next_due date
        next_due_str = request.form.get('next_due', '').strip()
        if next_due_str:
            try:
                schedule.next_due = datetime.strptime(next_due_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid next due date format.', 'error')
                return render_template('schedules/edit.html', machine=machine, schedule=schedule)

        # Parse last_completed date (optional manual override)
        last_completed_str = request.form.get('last_completed', '').strip()
        if last_completed_str:
            try:
                schedule.last_completed = datetime.strptime(last_completed_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid last completed date format.', 'error')
                return render_template('schedules/edit.html', machine=machine, schedule=schedule)
        else:
            schedule.last_completed = None

        try:
            db.session.commit()
            flash('Schedule updated successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating schedule: {str(e)}', 'error')

    return render_template('schedules/edit.html', machine=machine, schedule=schedule)


@schedules_bp.route('/<machine_id>/schedule/<int:id>/complete', methods=['POST'])
@login_required
@role_required('admin', 'engineer')
def complete_schedule(machine_id, id):
    """Mark a schedule as completed.
    Sets last_completed to today and auto-calculates the next_due date based on frequency.
    """
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    schedule = PreventiveSchedule.query.get_or_404(id)

    if schedule.machine_id != machine.id:
        flash('Schedule not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    today = datetime.utcnow().date()
    schedule.last_completed = today

    # Auto-calculate next_due based on frequency
    days_to_add = FREQUENCY_DAYS.get(schedule.frequency, 30)
    schedule.next_due = today + timedelta(days=days_to_add)

    try:
        db.session.commit()
        flash(f'Schedule marked as completed. Next due: {schedule.next_due.strftime("%Y-%m-%d")}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error completing schedule: {str(e)}', 'error')

    return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))


@schedules_bp.route('/<machine_id>/schedule/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_schedule(machine_id, id):
    """Delete a preventive schedule. Admin only."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    schedule = PreventiveSchedule.query.get_or_404(id)

    if schedule.machine_id != machine.id:
        flash('Schedule not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting schedule: {str(e)}', 'error')

    return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
