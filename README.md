# KanMind Backend

The **KanMind Backend** is a Django REST Framework (DRF) project that serves as an API for the [KanMind Frontend](https://github.com/Developer-Akademie-Backendkurs/project.KanMind?tab=readme-ov-file#kanmind-frontend-project).

It was developed as part of the **Developer Akademie** to help students with backend experience get started with smaller frontend integrations.

## Usage Note

This backend is a **development project** and runs on the Django Development Server (`python manage.py runserver`).
It is **not intended for production use**, as no security or deployment modifications have been made.
Its sole purpose is **learning and experimentation** as part of the **Developer Akademie**.

---

## Requirements

- **Python 3.10+**
- **pip** (Python package manager)
- **Django** and **Django REST Framework** (installed via `requirements.txt`)

---

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Lukas1979/kanmind_backend.git
   cd kanmind-backend

2. Create and activate a virtual environment
   It is recommended to use a virtual environment to manage dependencies.

   macOS / Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   Windows (PowerShell):
   ```bash
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Your terminal prompt should now show (.venv) indicating the virtual environment is active.

3. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt

4. Set up environment variables<br>
   If a .env.example file exists:
   ```bash
   cp .env.example .env
   ```
   Edit .env to configure settings like DEBUG, SECRET_KEY, ALLOWED_HOSTS, and database credentials.

   For development, you can use SQLite (default) and just set:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=127.0.0.1,localhost
   TIME_ZONE=Europe/Zurich
   ```
5. Apply database migrations
   ```bash
   python manage.py migrate
   ```
   If you have new model changes, create and apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to enter a username, email, and password. This user can log in to the Django admin.

7. Run the development server
   ```bash

   python manage.py runserver
   ```
   Open your browser at http://127.0.0.1:8000/
   to see the project running.

   To run on your local network:
   ```bash
   python manage.py runserver 0.0.0.0:8000

   ```
   Make sure to add your IP to ALLOWED_HOSTS in .env.

8. Access Django Admin
   
   Visit http://127.0.0.1:8000/admin/
   and log in using your superuser credentials.
