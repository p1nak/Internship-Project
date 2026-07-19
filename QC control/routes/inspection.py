from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
import os, uuid
from datetime import date
from werkzeug.utils import secure_filename
from routes.auth import login_required, role_required
from models import get_all_customers, create_panel, create_inspection, get_full_inspection
from config import Config

inspection_bp = Blueprint('inspection', __name__, url_prefix='/inspection')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@inspection_bp.route('/new', methods=['GET'])
@login_required
@role_required(['inspector', 'admin'])
def new_inspection():
    customers = get_all_customers()
    checklist_items = Config.CHECKLIST_ITEMS
    return render_template('inspection_form.html', customers=customers, checklist_items=checklist_items)


@inspection_bp.route('/submit', methods=['POST'])
@login_required
@role_required(['inspector', 'admin'])
def submit_inspection():
    try:
        # --- Extract form fields ---
        panel_id = request.form.get('panel_id', '').strip()
        panel_name = request.form.get('panel_name', '').strip()
        customer_id = request.form.get('customer_id', '').strip()
        project = request.form.get('project', '').strip()
        panel_type = request.form.get('panel_type', '').strip()
        drawing_no = request.form.get('drawing_no', '').strip()
        serial_no = request.form.get('serial_no', '').strip()

        # --- Validate required fields ---
        if not panel_id or not customer_id:
            flash('Panel ID and Customer are required.', 'error')
            return redirect(url_for('inspection.new_inspection'))

        # --- Inspection date (default to today) ---
        inspection_date = request.form.get('inspection_date', '').strip()
        if not inspection_date:
            inspection_date = date.today().isoformat()

        # --- Create the panel record ---
        panel_pk = create_panel(
            panel_id=panel_id,
            panel_name=panel_name,
            customer_id=int(customer_id),
            project=project,
            panel_type=panel_type,
            drawing_no=drawing_no,
            serial_no=serial_no,
        )

        # --- Build checklist results ---
        checklist_results = []
        for item in Config.CHECKLIST_ITEMS:
            slug = item.lower().replace(' ', '_')
            result = request.form.get(f'checklist_{slug}', 'pending')
            checklist_results.append((item, result))

        # --- Determine overall status ---
        results_only = [r for _, r in checklist_results]
        if 'fail' in results_only:
            status = 'fail'
        elif all(r == 'pass' for r in results_only):
            status = 'pass'
        else:
            status = 'pending'

        # --- Remarks ---
        remarks = request.form.get('remarks', '').strip()

        # --- Handle image uploads (max 3) ---
        image_paths = []
        files = request.files.getlist('images')
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        for f in files[:3]:
            if f and f.filename and allowed_file(f.filename):
                original_name = secure_filename(f.filename)
                saved_name = f"{uuid.uuid4().hex}_{original_name}"
                f.save(os.path.join(Config.UPLOAD_FOLDER, saved_name))
                image_paths.append((saved_name, original_name))

        # --- Persist the inspection ---
        inspection_id = create_inspection(
            panel_pk,
            session['user_id'],
            inspection_date,
            status,
            remarks,
            checklist_results,
            image_paths,
        )

        flash('Inspection submitted successfully!', 'success')
        return redirect(url_for('inspection.view_inspection', inspection_id=inspection_id))

    except Exception as e:
        flash(f'Error submitting inspection: {str(e)}', 'error')
        return redirect(url_for('inspection.new_inspection'))


@inspection_bp.route('/<int:inspection_id>', methods=['GET'])
@login_required
def view_inspection(inspection_id):
    data = get_full_inspection(inspection_id)
    if not data:
        flash('Inspection not found.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('inspection_detail.html', data=data)


@inspection_bp.route('/uploads/<filename>', methods=['GET'])
@login_required
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
