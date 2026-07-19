import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rhino-machines-qr-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'instance', 'qr_machine.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 256 * 1024 * 1024  # 256 MB
    QR_CODE_FOLDER = os.path.join(basedir, 'app', 'static', 'qrcodes')
    QR_BASE_URL = os.environ.get('QR_BASE_URL') or 'http://localhost:5000'
