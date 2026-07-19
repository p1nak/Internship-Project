"""
Digital Quality Control System — Main Application
QC Corporation
"""

from flask import Flask
from config import Config   
from models import init_db, seed_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure folders exist
    import os
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)

    # Initialize database
    init_db()
    seed_db()

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.inspection import inspection_bp
    from routes.search import search_bp
    from routes.admin import admin_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    # Inject config into templates
    @app.context_processor
    def inject_globals():
        return {
            'company_name': Config.COMPANY_NAME,
            'company_tagline': Config.COMPANY_TAGLINE,
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
