from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Machine, BreakdownRecord
from app.utils.decorators import role_required

breakdowns_bp = Blueprint('breakdowns', __name__, url_prefix='/machine')


@breakdowns_bp.route('/<machine_id>/breakdown/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer', 'supervisor')
def add_breakdown(machine_id):
    """Add a breakdown record for a machine."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()

    if request.method == 'POST':
        record = BreakdownRecord(
            machine_id=machine.id,
            problem=request.form.get('problem', '').strip(),
            root_cause=request.form.get('root_cause', '').strip(),
            solution=request.form.get('solution', '').strip(),
            engineer=request.form.get('engineer', '').strip(),
            created_by=current_user.username
        )

        # Parse downtime_minutes
        downtime_str = request.form.get('downtime_minutes', '').strip()
        if downtime_str:
            try:
                record.downtime_minutes = int(downtime_str)
            except ValueError:
                flash('Downtime must be a valid number.', 'error')
                return render_template('breakdowns/add.html', machine=machine)

        # Parse date
        date_str = request.form.get('date', '').strip()
        if date_str:
            try:
                record.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('breakdowns/add.html', machine=machine)
        else:
            flash('Breakdown date is required.', 'error')
            return render_template('breakdowns/add.html', machine=machine)

        try:
            db.session.add(record)
            db.session.commit()
            flash('Breakdown record added successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding breakdown record: {str(e)}', 'error')

    return render_template('breakdowns/add.html', machine=machine)


@breakdowns_bp.route('/<machine_id>/breakdown/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def edit_breakdown(machine_id, id):
    """Edit a breakdown record."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    record = BreakdownRecord.query.get_or_404(id)

    if record.machine_id != machine.id:
        flash('Record not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    if request.method == 'POST':
        record.problem = request.form.get('problem', record.problem).strip()
        record.root_cause = request.form.get('root_cause', '').strip()
        record.solution = request.form.get('solution', '').strip()
        record.engineer = request.form.get('engineer', record.engineer).strip()

        # Parse downtime_minutes
        downtime_str = request.form.get('downtime_minutes', '').strip()
        if downtime_str:
            try:
                record.downtime_minutes = int(downtime_str)
            except ValueError:
                flash('Downtime must be a valid number.', 'error')
                return render_template('breakdowns/edit.html', machine=machine, record=record)

        # Parse date
        date_str = request.form.get('date', '').strip()
        if date_str:
            try:
                record.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('breakdowns/edit.html', machine=machine, record=record)

        try:
            db.session.commit()
            flash('Breakdown record updated successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating breakdown record: {str(e)}', 'error')

    return render_template('breakdowns/edit.html', machine=machine, record=record)


@breakdowns_bp.route('/<machine_id>/breakdown/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_breakdown(machine_id, id):
    """Delete a breakdown record. Admin only."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    record = BreakdownRecord.query.get_or_404(id)

    if record.machine_id != machine.id:
        flash('Record not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    try:
        db.session.delete(record)
        db.session.commit()
        flash('Breakdown record deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting breakdown record: {str(e)}', 'error')

    return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
