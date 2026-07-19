from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Machine, MaintenanceRecord
from app.utils.decorators import role_required
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/machine')

@maintenance_bp.route('/<machine_id>/maintenance/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def add_maintenance(machine_id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    
    if request.method == 'POST':
        record = MaintenanceRecord(
            machine_id=machine.id,
            engineer=request.form.get('engineer'),
            work_done=request.form.get('work_done'),
            work_type=request.form.get('work_type'),
            notes=request.form.get('notes'),
            created_by=current_user.username
        )
        
        try:
            date_str = request.form.get('service_date')
            if date_str:
                record.service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
            next_date_str = request.form.get('next_service_date')
            if next_date_str:
                record.next_service_date = datetime.strptime(next_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
        db.session.add(record)
        db.session.commit()
        flash('Maintenance record added successfully', 'success')
        return redirect(url_for('machines.profile', machine_id=machine.machine_id) + '#maintenance')
        
    return render_template('maintenance/form.html', machine=machine, record=None)

@maintenance_bp.route('/<machine_id>/maintenance/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def edit_maintenance(machine_id, id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    record = MaintenanceRecord.query.get_or_404(id)
    
    if request.method == 'POST':
        record.engineer = request.form.get('engineer')
        record.work_done = request.form.get('work_done')
        record.work_type = request.form.get('work_type')
        record.notes = request.form.get('notes')
        
        try:
            date_str = request.form.get('service_date')
            if date_str:
                record.service_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
            next_date_str = request.form.get('next_service_date')
            if next_date_str:
                record.next_service_date = datetime.strptime(next_date_str, '%Y-%m-%d').date()
            else:
                record.next_service_date = None
        except ValueError:
            pass
            
        db.session.commit()
        flash('Maintenance record updated successfully', 'success')
        return redirect(url_for('machines.profile', machine_id=machine.machine_id) + '#maintenance')
        
    return render_template('maintenance/form.html', machine=machine, record=record)

@maintenance_bp.route('/<machine_id>/maintenance/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_maintenance(machine_id, id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    record = MaintenanceRecord.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    flash('Maintenance record deleted successfully', 'success')
    return redirect(url_for('machines.profile', machine_id=machine.machine_id) + '#maintenance')
