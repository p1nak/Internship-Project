from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():
    db.create_all()
    # Seed default admin
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            full_name='System Administrator',
            role='admin',
            department='IT'
        )
        db.session.add(admin)
        db.session.commit()
        print('Default admin user created (admin/admin123)')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
