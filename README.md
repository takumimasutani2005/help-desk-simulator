Help Desk Simulator
Project Overview
The Help Desk Simulator is a web-based application where users can submit support tickets and track their status, while administrators review, respond to, and manage those tickets. The system is designed to simulate a real help desk environment with role-based access, persistent storage, and multiple workflows.
This project was built for security analysis, so it intentionally includes vulnerabilities for testing and learning purposes.

System Description
The application is built using Python (Flask) with HTML templates and SQLite for data storage. It supports multiple users with different roles and allows interaction through forms and dynamic pages.
The system stores data in a SQLite database (helpdesk.db) and uses server-side logic to handle authentication, authorization, and ticket management.

User Roles
Regular User
Can register and log in
Can submit support tickets
Can view their own tickets and their status
Admin
Can view all submitted tickets
Can update ticket status (Open, In Progress, Closed)
Can respond to tickets
Can delete any ticket

Workflows
Workflow 1: User Submits a Ticket
User registers or logs in
User navigates to the "Submit Ticket" page
User fills out the form (title, description, priority)
Ticket is saved to the database
User sees the ticket appear on their dashboard
Workflow 2: Admin Reviews and Updates a Ticket
Admin logs in
Admin accesses the admin panel
Admin selects a ticket
Admin updates the ticket status and adds a response
Changes are saved and visible to the user
Features
User authentication (login/register)
Role-based access control (user vs admin)
Ticket submission with form validation
User dashboard to view submitted tickets
Admin panel to manage all tickets
Ticket detail view
Persistent database storage (SQLite)
File upload support for ticket attachments

Setup Instructions
Requirements
Python 3.10+
pip
Git
Local Setup
git clone 
cd helpdesk-simulator-vulnerable
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py


Default Admin Account
username: admin
password: i-love-cheese
Regular users must register through the Register page. Admin accounts are not publicly creatable.

Database
The application uses SQLite:
Users table (username, password, role)
Tickets table (title, description, status, priority, user_id)
To reset:
rm helpdesk.db
python3 app.py


Security Note
This application intentionally includes security vulnerabilities like SQL injection, broken access control, and unsafe file handling. It is intended for class analysis, not production use.
