# EFCC-Style Case Management System

A Django-based case management platform inspired by the EFCC (Economic and Financial Crimes Commission) workflow. It supports role-based access control, evidence management, intelligence reporting, and activity tracking for investigators, legal officers, analysts, and admins.

---

## Features

### Case Management
- Create, view, edit, and assign cases
- Track case status: Open → Investigating → Closed
- Full status change history with timestamps and notes
- Activity log per case (create, update, evidence upload, status change)

### Evidence Management
- Upload files as evidence linked to a case
- View and download evidence per case
- Tracks who uploaded each file and when

### Intelligence Module
- Manage intelligence sources (Human, Signal, Open Source, Cyber)
- Create intel reports linked to cases with type and status tracking
- Filter reports by type, status, and source reliability
- Geo-tagged reports with interactive Leaflet map
- Report summary view grouped by status
- PDF export of report summaries (requires GTK/Pango on Linux/macOS)

### User Roles
| Role | Access |
|------|--------|
| **Admin** | Full access — all cases, all users, assign cases |
| **Investigator** | View and edit assigned cases, upload evidence |
| **Legal Officer** | View assigned cases |
| **Analyst** | View assigned cases, create intel reports |

### Admin Dashboard
- Powered by [Jazzmin](https://django-jazzmin.readthedocs.io/) with a blue and white theme
- Manage users, cases, evidence, activity logs, intel sources and reports
- Custom filters, search, and date hierarchy on all models

---

## Tech Stack

- **Backend:** Django 5+
- **Database:** SQLite (default), easily swappable to PostgreSQL
- **Frontend:** Bootstrap 5, Chart.js, Leaflet.js
- **Admin UI:** Jazzmin
- **Tags:** django-taggit
- **Forms:** django-crispy-forms + crispy-bootstrap4
- **PDF:** WeasyPrint (optional, requires system GTK libraries)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/EFCC-Style-Case-Management-System.git
cd EFCC-Style-Case-Management-System-main
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django django-jazzmin django-crispy-forms crispy-bootstrap4 django-taggit Pillow weasyprint
```

> **Note:** WeasyPrint requires GTK/Pango system libraries for PDF generation.
> On Windows, PDF export will return a 503 message unless GTK is installed.
> See [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## Project Structure

```
EFCC-Style-Case-Management-System-main/
├── core/                        # Main app — users, cases, evidence, activity logs
│   ├── models.py                # User, Case, Evidence, ActivityLog, CaseStatusLog
│   ├── views.py                 # Case CRUD, dashboard, auth views
│   ├── forms.py                 # CaseForm, EvidenceForm, UserRegisterForm
│   ├── urls.py                  # Core URL patterns
│   ├── admin.py                 # Admin registrations
│   ├── decorators.py            # admin_or_assigned_required decorator
│   ├── utils.py                 # log_activity, role_redirect helpers
│   └── templatetags/            # Custom template filters (add_class, pluck)
│
├── intel/                       # Intelligence module
│   ├── models.py                # IntelligenceSource, IntelReport
│   ├── views.py                 # Source/report CRUD, dashboard, summary, PDF
│   ├── forms.py                 # IntelligenceSourceForm, IntelReportForm
│   ├── urls.py                  # Intel URL patterns
│   └── admin.py                 # Intel admin with custom PDF download
│
├── templates/                   # All HTML templates
│   ├── base.html                # Base layout with navbar
│   ├── dashboard.html           # Main dashboard
│   ├── case_*.html              # Case list, detail, form
│   ├── evidence_form.html       # Evidence upload
│   ├── login.html / register.html
│   ├── password_reset_*.html
│   └── intel/                   # Intelligence templates
│
├── efcc_case_system/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
│
├── manage.py
└── README.md
```

---

## URL Reference

| URL | Name | Description |
|-----|------|-------------|
| `/` | `dashboard` | Main dashboard |
| `/cases/` | `case_list` | List all cases |
| `/cases/new/` | `case_create` | Create a new case |
| `/cases/<pk>/` | `case_detail` | View case details |
| `/cases/<pk>/edit/` | `case_update` | Edit a case |
| `/case/<pk>/assign/` | `case_assign` | Assign a case (admin only) |
| `/cases/<id>/evidence/add/` | `add_evidence` | Upload evidence |
| `/intel/` | `intel_dashboard` | Intelligence dashboard |
| `/intel/sources/` | `source_list` | List intel sources |
| `/intel/sources/new/` | `source_create` | Add intel source |
| `/intel/reports/` | `report_list` | List intel reports |
| `/intel/reports/new/` | `report_create` | Add intel report |
| `/intel/summary/` | `report_summary` | Report summary by status |
| `/intel/summary/pdf/` | `download_report_pdf` | Download summary as PDF |
| `/login/` | `login` | Login page |
| `/logout/` | `logout` | Logout |
| `/register/` | `register` | Register new user |
| `/admin/` | — | Django admin panel |

---

## Default Roles

When registering, users can select one of the following roles:

- `admin` — Full system access
- `investigator` — Assigned case access
- `legal` — Legal officer access
- `analyst` — Analyst access

> To grant admin panel access, set `is_staff = True` on the user via the Django admin.

---

## Screenshots
<img width="1914" height="1079" alt="image" src="https://github.com/user-attachments/assets/5350bf5f-4830-4a38-8891-79c3c9c113c1" />

<img width="1916" height="1076" alt="image" src="https://github.com/user-attachments/assets/df9c5eb5-0a53-4871-8227-ce7d3d61136b" />

<img width="1898" height="1064" alt="image" src="https://github.com/user-attachments/assets/77d1b2ae-86a9-49b3-a587-be36e6ba4e30" />

<img width="1898" height="1079" alt="image" src="https://github.com/user-attachments/assets/91f8d310-3a2d-4f7b-8e63-27e672ba17c2" />

<img width="1911" height="1077" alt="image" src="https://github.com/user-attachments/assets/1b3d28cf-df7c-4c42-a1ed-8c059fe749a3" />

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/df4d4c33-7e1e-4d16-a5b9-12e1007f6016" />

<img width="1907" height="1079" alt="image" src="https://github.com/user-attachments/assets/accf55ee-1db1-48c1-ae93-d34c26608cad" />

<img width="1871" height="1079" alt="image" src="https://github.com/user-attachments/assets/329f4cbf-6d6d-4c82-a688-db0160bc2ddc" />

<img width="1900" height="1079" alt="image" src="https://github.com/user-attachments/assets/861a703b-9786-43cf-b304-39d86d111da7" />


> 

---

## License

This project is for educational and demonstration purposes.
