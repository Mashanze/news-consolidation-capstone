# Django News Application — Consolidation Capstone

A Django news publishing application developed for the HyperionDev M07T05 Consolidation Capstone.

## Features

- Reader, journalist, and editor roles
- News article management
- Publisher and newsletter functionality
- REST API endpoints
- MySQL database
- Docker deployment
- Sphinx documentation

## Requirements

- Python 3.9 or newer
- MySQL
- Docker Desktop (for containerized deployment)

## Local Installation

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Replace the placeholder secret key and configure the database credentials. For local commands, export database environment variables as needed.

Run database migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

## Docker Deployment

Configure your `.env` file with a Django secret key and database passwords.

Start the application:

```bash
docker compose up --build -d
```

Open http://localhost:8000

Stop the application:

```bash
docker compose down
```

## Testing

Run the tests inside Docker:

```bash
docker compose exec web python manage.py test
```

## Sphinx Documentation

Generated documentation is available at:

`docs/build/html/index.html`

To rebuild it:

```bash
pip install sphinx
python -m sphinx -b html docs/source docs/build/html
```

## Git Branches

- main — Final consolidated project
- docs — Python docstrings and Sphinx documentation
- container — Docker implementation

Both feature branches were merged into main.

## Security

The `.env` file is excluded from Git. Never commit passwords or secret keys.

The Docker configuration uses Django's development server and is intended for local development and assessment.# Django News Application

A Django-based news publishing platform developed for the
HyperionDev Software Engineering Capstone Project.

## Features

- User registration, login, and logout
- Reader, Journalist, and Editor account roles
- Administrator approval of requested editorial roles
- Article creation, editing, and publishing
- Editorial article approval
- Newsletter management
- Publisher and journalist subscriptions
- Django REST Framework API
- Token and session authentication
- Automated Django tests

## Technology Stack

- Python 3
- Django 4.2.30
- Django REST Framework 3.16.1
- MySQL
- PyMySQL

## Installation

Clone the project repository and navigate to the
directory containing manage.py.

Create a virtual environment:

    python3 -m venv .venv

Activate it on macOS or Linux:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## Database Setup

Install and start a compatible MySQL server.

Create the database:

    CREATE DATABASE news_db CHARACTER SET utf8mb4;

The development configuration currently expects:

- Database: news_db
- Username: root
- Host: localhost
- Port: 3306
- Password: empty

Update news_project/settings.py if your database
credentials differ.

Do not use an unrestricted root database account
in a production deployment.

## Environment Configuration

Create a .env file in the same directory as manage.py.

Generate a secret key:

    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Add the generated key to .env:

    DJANGO_SECRET_KEY=your-generated-secret-key

Keep .env private and never commit it to Git.

## Database Migrations

Run:

    python3 manage.py makemigrations --check

    python3 manage.py migrate

## Administrator Account

Create a superuser:

    python3 manage.py createsuperuser

## Running the Application

Start the development server:

    python3 manage.py runserver

Open:

    http://127.0.0.1:8000/

Django Admin:

    http://127.0.0.1:8000/admin/

## User Roles

### Reader

Readers can browse approved news content and
manage supported subscriptions.

### Journalist

Journalists can create and manage articles and
newsletters according to application permissions.

### Editor

Editors can review and approve submitted articles
according to application permissions.

### Registration and Role Approval

New users can request Reader, Journalist, or Editor.

All publicly registered accounts initially receive
Reader permissions.

Journalist and Editor requests must be approved
by an authorised superuser.

To approve a request:

1. Log into Django Admin as a superuser.
2. Open Custom users.
3. Review the requested_role column.
4. Select the relevant user.
5. Choose "Approve selected role requests".
6. Click Go.

Administrators can also reject pending requests.

## API

The application provides Django REST Framework
endpoints under:

    /api/

Authentication endpoints include:

    /api/token/

    /api-auth/login/

The API uses token and session authentication.
Access to endpoints depends on the configured
permissions.

## Testing

Run the complete automated test suite:

    python3 manage.py test

Run application tests:

    python3 manage.py test news_app

The current development test suite contains
26 passing tests.

## Development Notes

- DEBUG is enabled for local development.
- The application uses MySQL.
- The local .env file contains the Django secret key.
- Email notifications use Django's console email backend.
- The SQLite file, if present, is not the configured database.
- Production deployment requires separate security configuration.

## Security

Do not commit:

- .env files
- Secret keys
- Database passwords
- Local database files

Before production deployment, disable DEBUG,
configure ALLOWED_HOSTS, require a secret key,
use a restricted database user, and configure
HTTPS and secure cookie settings.

## Project Purpose

Developed as part of the HyperionDev
Software Engineering Bootcamp.
