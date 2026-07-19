import os
import tempfile
from flask import Blueprint, send_file, flash, redirect, url_for, current_app
from flask_login import login_required
from app.models import Machine
from app.utils.pdf_report import generate_machine_report

reports_bp = Blueprint('reports', __name__, url_prefix='/machine')


@reports_bp.route('/<machine_id>/report')
@login_required
def machine_report(machine_id):
    """Generate and download a PDF report for the machine.
    Available to any logged-in user.
    """
    machine = Machine.query.filter_by(machine_id=machine_id).first_or_404()

    try:
        # Generate the PDF report to a temporary file
        temp_dir = tempfile.mkdtemp()
        report_filename = f'{machine.machine_id}_report.pdf'
        report_path = os.path.join(temp_dir, report_filename)

        generate_machine_report(machine, report_path)

        response = send_file(
            report_path,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/pdf'
        )

        # Schedule cleanup after response is sent
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(report_path):
                    os.remove(report_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except OSError:
                pass

        return response

    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('machines.machine_profile', machine_id=machine.machine_id))
