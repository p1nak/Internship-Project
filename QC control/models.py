"""
Database models and CRUD operations for the Digital QC System.
Uses raw SQLite3 for simplicity — no ORM dependency.
"""

import sqlite3
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config


def get_db():
    """Get a database connection with row factory."""
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    """Create all tables if they don't exist."""
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)

    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'inspector',
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name VARCHAR(200) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS panels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id VARCHAR(50) NOT NULL,
            panel_name VARCHAR(200),
            customer_id INTEGER,
            project VARCHAR(200),
            panel_type VARCHAR(100),
            drawing_no VARCHAR(100),
            serial_no VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER NOT NULL,
            inspector_id INTEGER NOT NULL,
            inspection_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (panel_id) REFERENCES panels(id),
            FOREIGN KEY (inspector_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_id INTEGER NOT NULL,
            checklist_item VARCHAR(200) NOT NULL,
            result VARCHAR(10) NOT NULL DEFAULT 'pending',
            FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_id INTEGER NOT NULL,
            image_path VARCHAR(500) NOT NULL,
            original_name VARCHAR(200),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
        );
    ''')
    db.commit()
    db.close()


def seed_db():
    """Seed the database with default data if empty."""
    db = get_db()

    # Check if users exist
    user_count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'System Admin', 'admin', 'admin@rhino.com'),
            ('inspector', generate_password_hash('inspect123'), 'QC Inspector', 'inspector', 'inspector@rhino.com'),
            ('manager', generate_password_hash('manage123'), 'QC Manager', 'manager', 'manager@rhino.com'),
        ]
        db.executemany(
            'INSERT INTO users (username, password, full_name, role, email) VALUES (?, ?, ?, ?, ?)',
            users
        )

    # Check if customers exist
    cust_count = db.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    if cust_count == 0:
        customers = [
            ('Tata Motors Ltd.',),
            ('Larsen & Toubro',),
            ('Siemens India',),
            ('ABB India Ltd.',),
            ('Schneider Electric',),
        ]
        db.executemany('INSERT INTO customers (customer_name) VALUES (?)', customers)

    db.commit()
    db.close()


# ──────────────────────────────────────────────
# User operations
# ──────────────────────────────────────────────

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    return user


def get_user_by_username(username):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    db.close()
    return user


def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None


def get_all_users():
    db = get_db()
    users = db.execute('SELECT id, username, full_name, role, email, created_at FROM users ORDER BY id').fetchall()
    db.close()
    return users


def add_user(username, password, full_name, role, email=''):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, password, full_name, role, email) VALUES (?, ?, ?, ?, ?)',
            (username, generate_password_hash(password), full_name, role, email)
        )
        db.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        db.close()


def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ? AND role != "admin"', (user_id,))
    db.commit()
    db.close()


# ──────────────────────────────────────────────
# Customer operations
# ──────────────────────────────────────────────

def get_all_customers():
    db = get_db()
    customers = db.execute('SELECT * FROM customers ORDER BY customer_name').fetchall()
    db.close()
    return customers


def add_customer(name):
    db = get_db()
    try:
        db.execute('INSERT INTO customers (customer_name) VALUES (?)', (name,))
        db.commit()
        return True, "Customer added successfully."
    except sqlite3.IntegrityError:
        return False, "Customer already exists."
    finally:
        db.close()


def delete_customer(cust_id):
    db = get_db()
    db.execute('DELETE FROM customers WHERE id = ?', (cust_id,))
    db.commit()
    db.close()


def get_customer_by_id(cust_id):
    db = get_db()
    customer = db.execute('SELECT * FROM customers WHERE id = ?', (cust_id,)).fetchone()
    db.close()
    return customer


# ──────────────────────────────────────────────
# Panel operations
# ──────────────────────────────────────────────

def create_panel(panel_id, panel_name, customer_id, project, panel_type, drawing_no, serial_no):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO panels (panel_id, panel_name, customer_id, project, panel_type, drawing_no, serial_no)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (panel_id, panel_name, customer_id, project, panel_type, drawing_no, serial_no)
    )
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id


def get_panel_by_id(panel_pk):
    db = get_db()
    panel = db.execute('''
        SELECT p.*, c.customer_name
        FROM panels p
        LEFT JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
    ''', (panel_pk,)).fetchone()
    db.close()
    return panel


# ──────────────────────────────────────────────
# Inspection operations
# ──────────────────────────────────────────────

def create_inspection(panel_pk, inspector_id, inspection_date, status, remarks, checklist_results, image_paths):
    """
    Create a full inspection record with panel, checklist, and images.
    checklist_results: list of (item_name, 'pass'|'fail')
    image_paths: list of (file_path, original_name)
    Returns the new inspection ID.
    """
    db = get_db()
    try:
        cursor = db.execute(
            '''INSERT INTO inspections (panel_id, inspector_id, inspection_date, status, remarks)
               VALUES (?, ?, ?, ?, ?)''',
            (panel_pk, inspector_id, inspection_date, status, remarks)
        )
        inspection_id = cursor.lastrowid

        # Insert checklist items
        for item_name, result in checklist_results:
            db.execute(
                'INSERT INTO checklist (inspection_id, checklist_item, result) VALUES (?, ?, ?)',
                (inspection_id, item_name, result)
            )

        # Insert images
        for file_path, original_name in image_paths:
            db.execute(
                'INSERT INTO images (inspection_id, image_path, original_name) VALUES (?, ?, ?)',
                (inspection_id, file_path, original_name)
            )

        db.commit()
        return inspection_id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_inspection_by_id(inspection_id):
    db = get_db()
    inspection = db.execute('''
        SELECT i.*, p.panel_id as panel_code, p.panel_name, p.project, p.panel_type,
               p.drawing_no, p.serial_no, p.customer_id,
               c.customer_name, u.full_name as inspector_name
        FROM inspections i
        JOIN panels p ON i.panel_id = p.id
        LEFT JOIN customers c ON p.customer_id = c.id
        JOIN users u ON i.inspector_id = u.id
        WHERE i.id = ?
    ''', (inspection_id,)).fetchone()
    db.close()
    return inspection


def get_inspection_checklist(inspection_id):
    db = get_db()
    items = db.execute(
        'SELECT * FROM checklist WHERE inspection_id = ? ORDER BY id',
        (inspection_id,)
    ).fetchall()
    db.close()
    return items


def get_inspection_images(inspection_id):
    db = get_db()
    images = db.execute(
        'SELECT * FROM images WHERE inspection_id = ? ORDER BY id',
        (inspection_id,)
    ).fetchall()
    db.close()
    return images


def get_full_inspection(inspection_id):
    """Get inspection with all related data."""
    inspection = get_inspection_by_id(inspection_id)
    if not inspection:
        return None
    checklist = get_inspection_checklist(inspection_id)
    images = get_inspection_images(inspection_id)
    return {
        'inspection': dict(inspection),
        'checklist': [dict(item) for item in checklist],
        'images': [dict(img) for img in images],
    }


def get_recent_inspections(limit=10):
    db = get_db()
    inspections = db.execute('''
        SELECT i.id, i.inspection_date, i.status, i.created_at,
               p.panel_id as panel_code, p.panel_name,
               c.customer_name, u.full_name as inspector_name
        FROM inspections i
        JOIN panels p ON i.panel_id = p.id
        LEFT JOIN customers c ON p.customer_id = c.id
        JOIN users u ON i.inspector_id = u.id
        ORDER BY i.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    db.close()
    return inspections


def get_dashboard_stats():
    """Get statistics for the dashboard."""
    db = get_db()
    today = date.today().isoformat()

    total_today = db.execute(
        'SELECT COUNT(*) FROM inspections WHERE inspection_date = ?', (today,)
    ).fetchone()[0]

    passed = db.execute(
        'SELECT COUNT(*) FROM inspections WHERE status = "pass"'
    ).fetchone()[0]

    failed = db.execute(
        'SELECT COUNT(*) FROM inspections WHERE status = "fail"'
    ).fetchone()[0]

    pending = db.execute(
        'SELECT COUNT(*) FROM inspections WHERE status = "pending"'
    ).fetchone()[0]

    total = db.execute('SELECT COUNT(*) FROM inspections').fetchone()[0]

    db.close()
    return {
        'today': total_today,
        'passed': passed,
        'failed': failed,
        'pending': pending,
        'total': total,
    }


def search_inspections(panel_id=None, customer=None, project=None,
                       inspector=None, date_from=None, date_to=None,
                       status=None, page=1, per_page=20):
    """Search inspections with filters. Returns (results, total_count)."""
    db = get_db()

    conditions = []
    params = []

    if panel_id:
        conditions.append('p.panel_id LIKE ?')
        params.append(f'%{panel_id}%')
    if customer:
        conditions.append('c.customer_name LIKE ?')
        params.append(f'%{customer}%')
    if project:
        conditions.append('p.project LIKE ?')
        params.append(f'%{project}%')
    if inspector:
        conditions.append('u.full_name LIKE ?')
        params.append(f'%{inspector}%')
    if date_from:
        conditions.append('i.inspection_date >= ?')
        params.append(date_from)
    if date_to:
        conditions.append('i.inspection_date <= ?')
        params.append(date_to)
    if status:
        conditions.append('i.status = ?')
        params.append(status)

    where_clause = ' AND '.join(conditions) if conditions else '1=1'

    # Count total matching records
    count_sql = f'''
        SELECT COUNT(*)
        FROM inspections i
        JOIN panels p ON i.panel_id = p.id
        LEFT JOIN customers c ON p.customer_id = c.id
        JOIN users u ON i.inspector_id = u.id
        WHERE {where_clause}
    '''
    total = db.execute(count_sql, params).fetchone()[0]

    # Fetch paginated results
    offset = (page - 1) * per_page
    query_sql = f'''
        SELECT i.id, i.inspection_date, i.status, i.created_at,
               p.panel_id as panel_code, p.panel_name, p.project,
               c.customer_name, u.full_name as inspector_name
        FROM inspections i
        JOIN panels p ON i.panel_id = p.id
        LEFT JOIN customers c ON p.customer_id = c.id
        JOIN users u ON i.inspector_id = u.id
        WHERE {where_clause}
        ORDER BY i.created_at DESC
        LIMIT ? OFFSET ?
    '''
    params.extend([per_page, offset])
    results = db.execute(query_sql, params).fetchall()

    db.close()
    return [dict(r) for r in results], total


def delete_inspection(inspection_id):
    """Delete an inspection and its associated checklist and images."""
    db = get_db()
    # Get associated images to delete files
    images = db.execute('SELECT image_path FROM images WHERE inspection_id = ?', (inspection_id,)).fetchall()
    for img in images:
        filepath = os.path.join(Config.UPLOAD_FOLDER, img['image_path'])
        if os.path.exists(filepath):
            os.remove(filepath)
    # Cascade delete handles checklist and images
    db.execute('DELETE FROM inspections WHERE id = ?', (inspection_id,))
    db.commit()
    db.close()
    return images
