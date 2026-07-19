from app import create_app, db
from app.models import User, Machine, MaintenanceRecord, BreakdownRecord, SparePart, PreventiveSchedule
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
from app.utils.qr_generator import generate_qr
import os

app = create_app()

with app.app_context():
    # 1. Create Users
    print("Creating users...")
    users = [
        User(username='engineer1', password_hash=generate_password_hash('eng123'), full_name='Rahul Sharma', role='engineer', department='Maintenance'),
        User(username='super1', password_hash=generate_password_hash('sup123'), full_name='Amit Patel', role='supervisor', department='Production'),
        User(username='op1', password_hash=generate_password_hash('op123'), full_name='Raj Singh', role='operator', department='Shop Floor')
    ]
    
    for u in users:
        if not User.query.filter_by(username=u.username).first():
            db.session.add(u)
    db.session.commit()

    # 2. Create Machines
    print("Creating machines...")
    machines_data = [
        {
            'id': 'MCH001', 'name': 'Sand Reclamation Plant', 'dept': 'Foundry', 'type': 'Reclamation',
            'mfg': 'Rhino Machines', 'cap': '5 Ton/Hr', 'loc': 'Plant 1', 'status': 'active'
        },
        {
            'id': 'MCH002', 'name': 'Silica Plastic Block - SPB', 'dept': 'Recycling', 'type': 'Block Making',
            'mfg': 'Rhino Machines', 'cap': '1000 Blocks/Day', 'loc': 'Plant 2', 'status': 'active'
        },
        {
            'id': 'MCH003', 'name': 'RTC - Online Sand Controller', 'dept': 'Quality Control', 'type': 'Testing',
            'mfg': 'Rhino Machines', 'cap': 'Continuous', 'loc': 'Lab 1', 'status': 'active'
        },
        {
            'id': 'MCH004', 'name': 'MultiFlexFM High Pressure Moulding Machine', 'dept': 'Moulding', 'type': 'Moulding',
            'mfg': 'Rhino Machines', 'cap': '120 Moulds/Hr', 'loc': 'Plant 1', 'status': 'under_maintenance'
        },
        {
            'id': 'MCH005', 'name': 'Rotomax Mixer - Mixer Cooler', 'dept': 'Foundry', 'type': 'Mixing',
            'mfg': 'Rhino Machines', 'cap': '500 Kg/Batch', 'loc': 'Plant 1', 'status': 'inactive'
        }
    ]

    for m_data in machines_data:
        if not Machine.query.filter_by(machine_id=m_data['id']).first():
            m = Machine(
                machine_id=m_data['id'], machine_name=m_data['name'], department=m_data['dept'],
                machine_type=m_data['type'], manufacturer=m_data['mfg'], capacity=m_data['cap'],
                location=m_data['loc'], status=m_data['status'],
                purchase_date=date(2023, 5, 15), installation_date=date(2023, 6, 1)
            )
            
            # Generate QR
            qr_filename = generate_qr(m.machine_id, app.config['QR_BASE_URL'], app.config['QR_CODE_FOLDER'])
            m.qr_code_path = qr_filename
            
            db.session.add(m)
    
    db.session.commit()
    
    # 3. Create Records for MCH001
    print("Creating maintenance, breakdowns, spares, and schedules...")
    m1 = Machine.query.filter_by(machine_id='MCH001').first()
    m4 = Machine.query.filter_by(machine_id='MCH004').first()
    
    today = date.today()
    
    if m1:
        # Maintenance
        db.session.add(MaintenanceRecord(machine_id=m1.id, engineer='Rahul Sharma', service_date=today - timedelta(days=45), work_done='Changed conveyor belt and greased bearings', work_type='corrective'))
        db.session.add(MaintenanceRecord(machine_id=m1.id, engineer='Rahul Sharma', service_date=today - timedelta(days=15), work_done='Routine inspection, oil levels checked', work_type='preventive'))
        
        # Breakdowns
        db.session.add(BreakdownRecord(machine_id=m1.id, date=today - timedelta(days=20), problem='Motor overheated and tripped', root_cause='Dust accumulation in cooling fins', solution='Cleaned motor and reset thermal relay', downtime_minutes=120, engineer='Rahul Sharma'))
        
        # Spares
        db.session.add(SparePart(machine_id=m1.id, part_name='Conveyor Belt (5m)', part_number='CB-500', quantity=2, unit_cost=4500, min_stock_level=1, supplier='Beltech India'))
        db.session.add(SparePart(machine_id=m1.id, part_name='Main Bearing', part_number='BR-6205', quantity=0, unit_cost=850, min_stock_level=2, supplier='SKF')) # Low stock
        
        # Schedules
        db.session.add(PreventiveSchedule(machine_id=m1.id, task_description='Check bucket elevator alignment', frequency='Weekly', next_due=today + timedelta(days=3), assigned_to='Rahul Sharma'))
        db.session.add(PreventiveSchedule(machine_id=m1.id, task_description='Replace filter bags', frequency='Quarterly', next_due=today - timedelta(days=5), assigned_to='Rahul Sharma')) # Overdue

    if m4:
        db.session.add(BreakdownRecord(machine_id=m4.id, date=today - timedelta(days=2), problem='Hydraulic pressure drop during squeezing cycle', root_cause='Worn out seal in main cylinder', solution='Awaiting spare seal kits', downtime_minutes=2880, engineer='Rahul Sharma'))
        db.session.add(PreventiveSchedule(machine_id=m4.id, task_description='Inspect hydraulic lines for leaks', frequency='Weekly', next_due=today + timedelta(days=1), assigned_to='Amit Patel'))
        db.session.add(SparePart(machine_id=m4.id, part_name='Hydraulic Seal Kit', part_number='HS-1200', quantity=1, unit_cost=2500, min_stock_level=5, supplier='Parker')) # Low stock

    db.session.commit()
    print("Demo data successfully loaded!")
