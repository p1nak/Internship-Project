"""
Authentication routes for the Digital QC System.
Handles login, logout, session management, and access-control decorators.
"""

import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models import verify_user

auth_bp = Blueprint('auth', __name__)


# ──────────────────────────────────────────────
# Decorators
# ──────────────────────────────────────────────

def login_required(f):
    """Decorator that ensures the user is logged in."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(roles):
    """
    Decorator that restricts access to users whose role is in *roles*.
    Must be applied **after** login_required.

    Usage:
        @login_required
        @role_required(['admin', 'manager'])
        def some_view(): ...
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                flash('You are not authorized to access this page.', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@auth_bp.route('/')
def index():
    """Root route — redirect to dashboard if logged in, else to login."""
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login form and handle credential verification."""
    # Already logged in → go straight to dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        user = verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear the session and redirect to the login page."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
