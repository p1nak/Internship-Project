from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.utils.decorators import role_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('machines.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active_user:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            return redirect(url_for('machines.dashboard'))
            
        flash('Invalid username or password', 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
@role_required('admin')
def users():
    users_list = User.query.all()
    return render_template('auth/users.html', users=users_list)

@auth_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        department = request.form.get('department')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.add_user'))
            
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            department=department
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully', 'success')
        return redirect(url_for('auth.users'))
        
    return render_template('auth/user_form.html', user=None, form_title="Add User")

@auth_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.full_name = request.form.get('full_name')
        user.role = request.form.get('role')
        user.department = request.form.get('department')
        
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
            
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('auth.users'))
        
    return render_template('auth/user_form.html', user=user, form_title="Edit User")

@auth_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(id):
    if current_user.id == id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('auth.users'))
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('auth.users'))
