import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Machine, Document
from app.utils.decorators import role_required

documents_bp = Blueprint('documents', __name__, url_prefix='/machine')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route('/<machine_id>/documents/upload', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'engineer')
def upload_document(machine_id):
    """Upload a document for a machine."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()

    if request.method == 'POST':
        document_name = request.form.get('document_name', '').strip()
        document_type = request.form.get('document_type', 'other')

        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('documents/upload.html', machine=machine)

        file = request.files['file']

        if not file or not file.filename:
            flash('No file selected.', 'error')
            return render_template('documents/upload.html', machine=machine)

        if not allowed_file(file.filename):
            flash(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
            return render_template('documents/upload.html', machine=machine)

        if not document_name:
            flash('Document name is required.', 'error')
            return render_template('documents/upload.html', machine=machine)

        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', machine.machine_id)
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Get file size
        file_size = os.path.getsize(file_path)

        document = Document(
            machine_id=machine.id,
            document_name=document_name,
            document_type=document_type,
            file_path=f'uploads/documents/{machine.machine_id}/{filename}',
            file_size=file_size,
            uploaded_by=current_user.username
        )

        try:
            db.session.add(document)
            db.session.commit()
            flash(f'Document "{document_name}" uploaded successfully.', 'success')
            return redirect(url_for('machines.profile', machine_id=machine.machine_id))
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Error uploading document: {str(e)}', 'error')

    return render_template('documents/upload.html', machine=machine)


@documents_bp.route('/<machine_id>/documents/<int:id>/download')
def download_document(machine_id, id):
    """Download a document. Available to any logged-in user."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    document = Document.query.get_or_404(id)

    if document.machine_id != machine.id:
        abort(404)

    file_path = os.path.join(current_app.root_path, '..', document.file_path)

    if not os.path.exists(file_path):
        flash('File not found on server.', 'error')
        return redirect(url_for('machines.profile', machine_id=machine.machine_id))

    is_inline = request.args.get('inline', '0') == '1'

    return send_file(
        file_path,
        as_attachment=not is_inline,
        download_name=document.document_name + os.path.splitext(document.file_path)[1]
    )


@documents_bp.route('/<machine_id>/documents/<int:id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'engineer')
def delete_document(machine_id, id):
    """Delete a document and its file. Admin and engineer only."""
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()
    document = Document.query.get_or_404(id)

    if document.machine_id != machine.id:
        flash('Document not found for this machine.', 'error')
        return redirect(url_for('machines.profile', machine_id=machine.machine_id))

    try:
        # Delete physical file
        file_path = os.path.join(current_app.root_path, '..', document.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        doc_name = document.document_name
        db.session.delete(document)
        db.session.commit()
        flash(f'Document "{doc_name}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting document: {str(e)}', 'error')

    return redirect(url_for('machines.profile', machine_id=machine.machine_id))
