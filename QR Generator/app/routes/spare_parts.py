from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Machine, SparePart
from app.utils.decorators import role_required

spare_parts_bp = Blueprint('spare_parts', __name__, url_prefix='/machine')


@spare_parts_bp.route('/<machine_id>/spares/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def add_spare_part(machine_id):
    """Add a spare part for a machine."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()

    if request.method == 'POST':
        part = SparePart(
            machine_id=machine.id,
            part_name=request.form.get('part_name', '').strip(),
            part_number=request.form.get('part_number', '').strip(),
            supplier=request.form.get('supplier', '').strip()
        )

        # Parse numeric fields
        try:
            quantity_str = request.form.get('quantity', '0').strip()
            part.quantity = int(quantity_str) if quantity_str else 0
        except ValueError:
            flash('Quantity must be a valid number.', 'error')
            return render_template('spare_parts/add.html', machine=machine)

        try:
            cost_str = request.form.get('unit_cost', '0').strip()
            part.unit_cost = float(cost_str) if cost_str else 0.0
        except ValueError:
            flash('Unit cost must be a valid number.', 'error')
            return render_template('spare_parts/add.html', machine=machine)

        try:
            min_stock_str = request.form.get('min_stock_level', '0').strip()
            part.min_stock_level = int(min_stock_str) if min_stock_str else 0
        except ValueError:
            flash('Minimum stock level must be a valid number.', 'error')
            return render_template('spare_parts/add.html', machine=machine)

        if not part.part_name:
            flash('Part name is required.', 'error')
            return render_template('spare_parts/add.html', machine=machine)

        try:
            db.session.add(part)
            db.session.commit()
            flash(f'Spare part "{part.part_name}" added successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding spare part: {str(e)}', 'error')

    return render_template('spare_parts/add.html', machine=machine)


@spare_parts_bp.route('/<machine_id>/spares/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def edit_spare_part(machine_id, id):
    """Edit a spare part."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    part = SparePart.query.get_or_404(id)

    if part.machine_id != machine.id:
        flash('Spare part not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    if request.method == 'POST':
        part.part_name = request.form.get('part_name', part.part_name).strip()
        part.part_number = request.form.get('part_number', '').strip()
        part.supplier = request.form.get('supplier', '').strip()

        try:
            quantity_str = request.form.get('quantity', '0').strip()
            part.quantity = int(quantity_str) if quantity_str else 0
        except ValueError:
            flash('Quantity must be a valid number.', 'error')
            return render_template('spare_parts/edit.html', machine=machine, part=part)

        try:
            cost_str = request.form.get('unit_cost', '0').strip()
            part.unit_cost = float(cost_str) if cost_str else 0.0
        except ValueError:
            flash('Unit cost must be a valid number.', 'error')
            return render_template('spare_parts/edit.html', machine=machine, part=part)

        try:
            min_stock_str = request.form.get('min_stock_level', '0').strip()
            part.min_stock_level = int(min_stock_str) if min_stock_str else 0
        except ValueError:
            flash('Minimum stock level must be a valid number.', 'error')
            return render_template('spare_parts/edit.html', machine=machine, part=part)

        try:
            db.session.commit()
            flash(f'Spare part "{part.part_name}" updated successfully.', 'success')
            return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating spare part: {str(e)}', 'error')

    return render_template('spare_parts/edit.html', machine=machine, part=part)


@spare_parts_bp.route('/<machine_id>/spares/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_spare_part(machine_id, id):
    """Delete a spare part. Admin only."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    part = SparePart.query.get_or_404(id)

    if part.machine_id != machine.id:
        flash('Spare part not found for this machine.', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))

    try:
        part_name = part.part_name
        db.session.delete(part)
        db.session.commit()
        flash(f'Spare part "{part_name}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting spare part: {str(e)}', 'error')

    return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
