import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'rhino-qc-secret-key-change-in-production')
    DATABASE = os.path.join(BASE_DIR, 'database', 'qc.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_IMAGES_PER_INSPECTION = 3
    COMPANY_NAME = 'QC Corporation'
    COMPANY_TAGLINE = 'Quality Beyond Standards'

    # QC Checklist items — order matters for the report
    CHECKLIST_ITEMS = [
        'Wiring Checked',
        'Wire Ferrules Proper',
        'Terminal Tightening',
        'Component Placement',
        'Component Rating',
        'MCB Installed Properly',
        'Contactor Wiring',
        'Relay Wiring',
        'Earthing Connected',
        'Labels Available',
        'Cable Dressing',
        'Nut Bolt Tightening',
        'Voltage Test',
        'Functional Test',
        'Insulation Test',
        'Visual Inspection',
    ]
