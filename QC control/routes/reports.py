"""
Reports module for Digital QC System.
Handles PDF report generation and download for inspection records.
"""

import os
from flask import Blueprint, redirect, url_for, flash, send_from_directory
from routes.auth import login_required
from models import get_full_inspection
from utils.pdf_generator import generate_pdf
from config import Config

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/<int:inspection_id>')
@login_required
def generate_report(inspection_id):
    """Generate and download a PDF report for a specific inspection."""
    try:
        # Fetch complete inspection data
        inspection_data = get_full_inspection(inspection_id)

        if not inspection_data:
            flash('Inspection record not found.', 'error')
            return redirect(url_for('dashboard.dashboard'))

        # Build filename from panel code and date
        inspection = inspection_data['inspection']
        panel_code = inspection.get('panel_code', 'unknown').replace(' ', '_').replace('/', '-')
        date_str = inspection.get('inspection_date', 'nodate').replace('-', '')
        filename = f'QC_Report_{panel_code}_{date_str}.pdf'

        # Ensure report folder exists
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)

        # Build output path and generate PDF
        output_path = os.path.join(Config.REPORT_FOLDER, filename)
        generate_pdf(inspection_data, output_path)

        # Send the generated file
        return send_from_directory(
            Config.REPORT_FOLDER,
            filename,
            as_attachment=True
        )

    except Exception as e:
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('dashboard.dashboard'))
