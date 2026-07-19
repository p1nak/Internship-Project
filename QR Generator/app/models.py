from app import db
from flask_login import UserMixin
from datetime import datetime, date


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')  # admin, engineer, supervisor, operator
    department = db.Column(db.String(100))
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g. MCH001
    machine_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    machine_type = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    capacity = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    installation_date = db.Column(db.Date)
    location = db.Column(db.String(200))
    image_path = db.Column(db.String(500))
    qr_code_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')  # active, inactive, under_maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    maintenance_records = db.relationship('MaintenanceRecord', backref='machine', lazy=True, cascade='all, delete-orphan')
    breakdown_records = db.relationship('BreakdownRecord', backref='machine', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='machine', lazy=True, cascade='all, delete-orphan')
    spare_parts = db.relationship('SparePart', backref='machine', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('PreventiveSchedule', backref='machine', lazy=True, cascade='all, delete-orphan')


class MaintenanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    engineer = db.Column(db.String(120), nullable=False)
    service_date = db.Column(db.Date, nullable=False, default=date.today)
    work_done = db.Column(db.Text, nullable=False)
    work_type = db.Column(db.String(20), default='corrective')  # preventive, corrective
    next_service_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BreakdownRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    problem = db.Column(db.Text, nullable=False)
    root_cause = db.Column(db.Text)
    solution = db.Column(db.Text)
    downtime_minutes = db.Column(db.Integer, default=0)
    engineer = db.Column(db.String(120))
    created_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    document_name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), default='other')  # manual, drawing, sop, safety, plc, other
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    uploaded_by = db.Column(db.String(80))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    part_name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=0)
    unit_cost = db.Column(db.Float, default=0.0)
    supplier = db.Column(db.String(200))
    min_stock_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PreventiveSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    task_description = db.Column(db.String(500), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    last_completed = db.Column(db.Date)
    next_due = db.Column(db.Date, nullable=False)
    assigned_to = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
