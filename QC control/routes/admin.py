"""
Admin module for Digital QC System.
Provides user management, customer management, and system administration.
"""

import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from routes.auth import login_required, role_required
from models import (
    get_all_users,
    add_user,
    delete_user,
    get_all_customers,
    add_customer,
    delete_customer,
    get_dashboard_stats
)
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@role_required(['admin'])
def admin_panel():
    """Main admin panel with users, customers, and system stats."""
    users = get_all_users()
    customers = get_all_customers()
    stats = get_dashboard_stats()
    return render_template(
        'admin.html',
        users=users,
        customers=customers,
        stats=stats
    )


@admin_bp.route('/users/add', methods=['POST'])
@login_required
@role_required(['admin'])
def add_user_route():
    """Add a new user to the system."""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'inspector').strip()
    email = request.form.get('email', '').strip()

    if not username or not password or not full_name:
        flash('Username, password, and full name are required.', 'error')
        return redirect(url_for('admin.admin_panel'))

    success, message = add_user(
        username=username,
        password=password,
        full_name=full_name,
        role=role,
        email=email
    )

    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_user_route(user_id):
    """Delete a user from the system."""
    success, message = delete_user(user_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/customers/add', methods=['POST'])
@login_required
@role_required(['admin'])
def add_customer_route():
    """Add a new customer."""
    customer_name = request.form.get('customer_name', '').strip()

    if not customer_name:
        flash('Customer name is required.', 'error')
        return redirect(url_for('admin.admin_panel'))

    success, message = add_customer(customer_name)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/customers/delete/<int:cust_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_customer_route(cust_id):
    """Delete a customer."""
    success, message = delete_customer(cust_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/backup')
@login_required
@role_required(['admin'])
def backup_db():
    """Download a backup of the database file."""
    try:
        db_directory = os.path.dirname(Config.DATABASE)
        db_filename = os.path.basename(Config.DATABASE)
        download_name = f'qc_backup_{datetime.now():%Y%m%d_%H%M%S}.db'

        return send_from_directory(
            db_directory,
            db_filename,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'error')
        return redirect(url_for('admin.admin_panel'))
