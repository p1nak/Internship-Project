"""
Search module for Digital QC System.
Provides advanced search and filtering for inspection records.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from models import search_inspections
from math import ceil

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
@login_required
def search_page():
    """Advanced search page with multi-field filtering and pagination."""
    # Get query parameters
    panel_id = request.args.get('panel_id', '').strip()
    customer = request.args.get('customer', '').strip()
    project = request.args.get('project', '').strip()
    inspector = request.args.get('inspector', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    results = []
    total = 0
    total_pages = 0
    per_page = 20

    # Only search if at least one filter is provided
    has_filters = any([panel_id, customer, project, inspector, date_from, date_to, status])

    if has_filters:
        results, total = search_inspections(
            panel_id=panel_id,
            customer=customer,
            project=project,
            inspector=inspector,
            date_from=date_from,
            date_to=date_to,
            status=status,
            page=page,
            per_page=per_page
        )
        total_pages = ceil(total / per_page) if total > 0 else 0

    return render_template(
        'search.html',
        results=results,
        total=total,
        total_pages=total_pages,
        page=page,
        panel_id=panel_id,
        customer=customer,
        project=project,
        inspector=inspector,
        date_from=date_from,
        date_to=date_to,
        status=status,
        has_filters=has_filters
    )
