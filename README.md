# Trek Management System

A simple Flask-based web application for managing trekking packages, bookings, staff approvals, and user accounts.

## Overview

This project allows three types of users to interact with the system:

- Admin: manages staff approvals, creates or edits treks, and views all bookings.
- Staff: handles assigned treks, updates status and available slots, and views participants.
- Trekkers/Users: browse available treks, book seats, and manage their own bookings.

## Features

- User registration and login
- Staff registration that requires admin approval
- Role-based access for admin, staff, and trekkers
- Trek catalog with search and difficulty filters
- Trek booking with overbooking protection
- User dashboard for active bookings and booking history
- Staff dashboard for assigned treks and participant tracking
- Admin dashboard for managing users, treks, and bookings

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- Jinja2 templates
- Bootstrap 5

## Project Structure

- app/ - main Flask application package
  - models.py - database models
  - routes/ - role-based route handlers
  - templates/ - HTML templates
- run.py - entry point for running the application
- requirements.txt - Python dependencies
- api.yaml - OpenAPI specification for the application endpoints

## How to Run the Project

### 1. Open the project folder

In your terminal, move into the project directory:

```bash
cd C:\Users\Mathe\Downloads\MAD1-trek_manager
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python run.py
```

The app will start in development mode and usually be available at:

```text
http://127.0.0.1:5000/
```

### 5. Use the application

Open the URL in your browser.

You can log in with the default admin account:

- Username: admin
- Password: admin123

## Notes

- The first time the app runs, it will create the SQLite database file automatically.
- The admin account is seeded automatically if it does not already exist.
- To stop the server, press Ctrl + C in the terminal.

## API Reference

An OpenAPI specification is available in [api.yaml](api.yaml).
