# SmartHealth

SmartHealth is a Flask-based healthcare appointment web app that helps patients find doctors, book visits, and track appointments in one place. It includes a public landing page, doctor search, appointment booking, patient login/registration, and an admin dashboard for managing doctors, users, and appointments.

## Preview

Add screenshots here before publishing if you want the repository page to look even stronger on GitHub.

## Features

- Doctor search by name, specialty, or city.
- Appointment booking with confirmation flow.
- Patient authentication with registration and login.
- Appointment history for logged-in users.
- Admin dashboard to manage doctors, users, and bookings.
- Responsive UI built with Bootstrap and custom styling.

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5
- Jinja2 templates

## Project Structure

- `app.py` contains the Flask app, routes, models, and database setup.
- `templates/` contains the HTML templates for the public site and dashboard pages.
- `static/css/style.css` contains the custom styling.
- `static/img/` contains the design assets used by the site.

## Local Setup

1. Create and activate a virtual environment.
2. Install the dependencies used by the project.
3. Run the Flask app.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask flask_sqlalchemy werkzeug
python app.py
```

The app will start on the default Flask development server.

## Demo Access

Use the email address below as the username.

- Admin: `admin@smarthealth.local`
- Admin password: `SmartHealthAdmin123!`
- Patient: `patient@smarthealth.local`
- Patient password: `SmartHealthPatient123!`

## Notes

- The database is created automatically on first launch.
- If you add your own screenshots, place them in the repository and reference them in the preview section.

## License

No license has been specified yet.