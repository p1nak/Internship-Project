"""
Dashboard routes for the Digital QC System.
Displays summary statistics and recent inspection activity.
"""

from flask import Blueprint, render_template

from routes.auth import login_required
from models import get_dashboard_stats, get_recent_inspections

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard():
    """Main dashboard view with stats and recent inspections."""
    stats = get_dashboard_stats()
    recent_inspections = get_recent_inspections(limit=10)
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_inspections=recent_inspections,
    )
