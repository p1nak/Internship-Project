import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.machines import machines_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.breakdowns import breakdowns_bp
    from app.routes.documents import documents_bp
    from app.routes.spare_parts import spare_parts_bp
    from app.routes.schedules import schedules_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(machines_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(breakdowns_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(spare_parts_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(reports_bp)

    # Create upload directories on startup
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_CODE_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    return app
