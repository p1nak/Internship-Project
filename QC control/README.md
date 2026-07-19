# Digital Quality Control System

A comprehensive, web-based Quality Control (QC) management system designed for **QC Corporation** to streamline the inspection of Electrical Control Panels.

## Features

- **Role-Based Access Control:** Secure login system with distinct permissions for Admins, Managers, and Inspectors.
- **Dynamic Dashboard:** Real-time statistics tracking daily inspections, passed panels, failures, and pending checks.
- **Digital Inspection Forms:** Step-by-step wizard for capturing panel details, completing standardized QC checklists, and recording inspector remarks.
- **Defect Photo Gallery:** Integrated drag-and-drop image upload supporting up to 3 defect photos per inspection with interactive hover-zoom previews.
- **Premium UI/UX:** Built with Bootstrap 5 and custom CSS. Features a sleek Glassmorphism design, custom pill badges for checklist statuses, and a seamless Dark/Light mode theme toggle.
- **Print Optimization:** Dedicated print styling ensuring inspection reports automatically format perfectly onto physical A4 paper without wasting ink on dark mode backgrounds.
- **Search & Filter:** Advanced search page to quickly locate past inspections by Panel ID, Customer, Project, or Status.
- **Admin Panel:** Centralized management of user accounts and customer directories.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite3 (Raw SQL, no ORM overhead)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5.3, Bootstrap Icons
- **Security:** Werkzeug password hashing

## Installation & Setup

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd "QC control"
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   *The database (`qc_system.db`) and default folders will be automatically initialized on first run.*

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Default Credentials

The system automatically seeds the database with the following default accounts on the first run:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Manager** | `manager` | `manage123` |
| **Inspector**| `inspector`| `inspect123` |

*(Note: It is highly recommended to change these passwords or delete default accounts in a production environment via the Admin Panel).*

## Project Structure

```
├── app.py                 # Main Flask application and server entry point
├── config.py              # Application configuration and constants
├── models.py              # Database connection and raw SQL queries
├── routes/                # Blueprint modules for routing (auth, dashboard, inspection, admin)
├── static/                # Static assets
│   ├── css/style.css      # Core stylesheet containing premium UI and theme variables
│   ├── js/main.js         # Frontend interactivity (theme toggle, image uploads)
│   └── img/               # Image assets (logos, placeholders)
├── templates/             # Jinja2 HTML templates
├── database/              # SQLite database storage (auto-generated)
└── uploads/               # Uploaded defect images (auto-generated)
```

## License
&copy; 2026 QC Corporation. All rights reserved.
