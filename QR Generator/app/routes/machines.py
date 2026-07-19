from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Machine, PreventiveSchedule, BreakdownRecord, SparePart
from app.utils.decorators import role_required
from app.utils.qr_generator import generate_qr
from datetime import datetime, date, timedelta
import os

machines_bp = Blueprint('machines', __name__, url_prefix='/')

@machines_bp.route('/machine/image/<filename>')
def machine_image(filename):
    from flask import send_from_directory
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'machines')
    return send_from_directory(upload_dir, filename)

@machines_bp.route('/')
@login_required
def dashboard():
    total_machines = Machine.query.count()
    
    # Calculate due services (next_due <= today + 7 days)
    today = date.today()
    seven_days_from_now = today + timedelta(days=7)
    due_service_count = PreventiveSchedule.query.filter(
        PreventiveSchedule.is_active == True,
        PreventiveSchedule.next_due <= seven_days_from_now
    ).count()
    
    # Recent breakdowns (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_breakdown_count = BreakdownRecord.query.filter(
        BreakdownRecord.date >= thirty_days_ago
    ).count()
    
    # Low stock parts
    low_stock_count = SparePart.query.filter(
        SparePart.quantity <= SparePart.min_stock_level
    ).count()
    
    # Upcoming schedules (next 10)
    upcoming_schedules = PreventiveSchedule.query.filter_by(is_active=True)\
        .order_by(PreventiveSchedule.next_due.asc())\
        .limit(10).all()
        
    # Recent breakdowns (last 5)
    recent_breakdowns = BreakdownRecord.query\
        .order_by(BreakdownRecord.date.desc())\
        .limit(5).all()
        
    return render_template('dashboard.html', 
                          total_machines=total_machines,
                          due_service_count=due_service_count,
                          recent_breakdown_count=recent_breakdown_count,
                          low_stock_count=low_stock_count,
                          upcoming_schedules=upcoming_schedules,
                          recent_breakdowns=recent_breakdowns,
                          now=today)

@machines_bp.route('/machines')
@login_required
def list():
    search_query = request.args.get('q', '')
    selected_department = request.args.get('department', '')
    
    query = Machine.query
    
    if search_query:
        query = query.filter(
            db.or_(
                Machine.machine_id.ilike(f'%{search_query}%'),
                Machine.machine_name.ilike(f'%{search_query}%'),
                Machine.manufacturer.ilike(f'%{search_query}%')
            )
        )
        
    if selected_department:
        query = query.filter_by(department=selected_department)
        
    machines = query.all()
    
    # Get unique departments for filter dropdown
    departments = [d[0] for d in db.session.query(Machine.department).distinct().all() if d[0]]
    
    return render_template('machines/list.html', 
                          machines=machines, 
                          departments=departments,
                          search_query=search_query,
                          selected_department=selected_department)

@machines_bp.route('/machines/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_machine():
    if request.method == 'POST':
        machine_id = request.form.get('machine_id')
        
        if Machine.query.filter_by(machine_id=machine_id).first():
            flash('Machine ID already exists', 'danger')
            return redirect(url_for('machines.add_machine'))
            
        machine = Machine(
            machine_id=machine_id,
            machine_name=request.form.get('machine_name'),
            department=request.form.get('department'),
            machine_type=request.form.get('machine_type'),
            manufacturer=request.form.get('manufacturer'),
            model=request.form.get('model'),
            serial_number=request.form.get('serial_number'),
            capacity=request.form.get('capacity'),
            location=request.form.get('location'),
            status=request.form.get('status', 'active')
        )
        
        try:
            purchase_date_str = request.form.get('purchase_date')
            if purchase_date_str:
                machine.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                
            install_date_str = request.form.get('installation_date')
            if install_date_str:
                machine.installation_date = datetime.strptime(install_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                new_filename = f"{machine_id}{ext}"
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'machines')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, new_filename))
                machine.image_path = new_filename
                
        # Generate QR Code
        qr_filename = generate_qr(
            machine.machine_id, 
            current_app.config['QR_BASE_URL'], 
            current_app.config['QR_CODE_FOLDER']
        )
        machine.qr_code_path = qr_filename
        
        db.session.add(machine)
        db.session.commit()
        
        flash('Machine added successfully', 'success')
        return redirect(url_for('machines.list'))
        
    return render_template('machines/add.html')

@machines_bp.route('/machine/<machine_id>')
def profile(machine_id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    
    today = date.today()
    next_schedule = PreventiveSchedule.query.filter(
        PreventiveSchedule.machine_id == machine.id,
        PreventiveSchedule.is_active == True
    ).order_by(PreventiveSchedule.next_due.asc()).first()
    
    days_until_service = None
    if next_schedule:
        days_until_service = (next_schedule.next_due - today).days
        
    return render_template('machines/profile.html', 
                          machine=machine,
                          next_schedule=next_schedule,
                          days_until_service=days_until_service,
                          now=today)

@machines_bp.route('/machine/<machine_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_machine(machine_id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    
    if request.method == 'POST':
        machine.machine_name = request.form.get('machine_name')
        machine.department = request.form.get('department')
        machine.machine_type = request.form.get('machine_type')
        machine.manufacturer = request.form.get('manufacturer')
        machine.model = request.form.get('model')
        machine.serial_number = request.form.get('serial_number')
        machine.capacity = request.form.get('capacity')
        machine.location = request.form.get('location')
        machine.status = request.form.get('status')
        
        try:
            purchase_date_str = request.form.get('purchase_date')
            if purchase_date_str:
                machine.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
            else:
                machine.purchase_date = None
                
            install_date_str = request.form.get('installation_date')
            if install_date_str:
                machine.installation_date = datetime.strptime(install_date_str, '%Y-%m-%d').date()
            else:
                machine.installation_date = None
        except ValueError:
            pass
            
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                new_filename = f"{machine.machine_id}{ext}"
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'machines')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, new_filename)
                file.save(file_path)
                machine.image_path = new_filename
                
        db.session.commit()
        flash('Machine updated successfully', 'success')
        return redirect(url_for('machines.profile', machine_id=machine.machine_id))
        
    return render_template('machines/edit.html', machine=machine)

@machines_bp.route('/machine/<machine_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_machine(machine_id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    
    # Delete uploaded files (image, qr code, documents)
    if machine.image_path:
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'machines', machine.image_path)
        if os.path.exists(img_path):
            os.remove(img_path)
            
    if machine.qr_code_path:
        qr_path = os.path.join(current_app.config['QR_CODE_FOLDER'], machine.qr_code_path)
        if os.path.exists(qr_path):
            os.remove(qr_path)
            
    doc_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', str(machine.id))
    if os.path.exists(doc_dir):
        import shutil
        shutil.rmtree(doc_dir)
        
    db.session.delete(machine)
    db.session.commit()
    flash('Machine deleted successfully', 'success')
    return redirect(url_for('machines.list'))

@machines_bp.route('/machine/<machine_id>/qr')
@login_required
def qr_print(machine_id):
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    return render_template('machines/qr_print.html', machine=machine)
