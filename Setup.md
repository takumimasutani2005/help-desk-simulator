# Setup Instructions

## Requirements

- Python 3.10+
- pip
- Git

## Local Setup
download the zip "helpdesk-simulator-vulnerable 2.zip"
```bash
cd helpdesk-simulator-vulnerable
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open the application at:

```text
http://127.0.0.1:5000
```

## Default Admin Account

```text
username: admin
password: i-love-cheese
```

Student users must be created through the Register page. Registration always creates a regular user account. The app does not allow public admin registration.

## Resetting the Database

The SQLite database is created automatically as `helpdesk.db`.

To reset the app:

```bash
rm helpdesk.db
python3 app.py
```

## Notes

This project intentionally contains security vulnerabilities for classroom analysis. Do not deploy it publicly.
