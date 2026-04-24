# AI Usage Documentation

## AI Tools Used

- ChatGPT was used to help generate the Flask application structure with html and css as well. ChatGPT was also used for setup instructions.

## AI-Generated vs Manually Written Components

| Component | Source | Notes |
|---|---|---|
| Flask app structure | AI + manual review | AI created routes, models, and basic workflow, manually went in to ensure vulnerabilities were able to be exploited |
| SQLAlchemy models | AI | Models were generated to match project requirements. |
| Authentication routes | AI + manual review | Login, logout, and registration were created by AI. I manually went in and made sure admin account could not be created as a drop down menu option and there was no default bad admin password |
| Admin-only seeded account | AI + Manual | AI made it so you could have multiple accounts. Went in to make sure only one was available |
| Student registration restriction | AI + Manual | Registration creates only regular users. |
| HTML templates | AI | Templates were generated and edited to match route names. |
| CSS styling | AI-generated | Basic styling|
| Documentation | AI + manual review | Setup doc was generated, readme, ai_usage and the video are done manually|
| Intentional vulnerabilities | AI + manual review | Vulnerabilities were added for classroom security analysis manually and AI assisted|

## Example Prompts Used

### Prompt 1

> Build a small Flask help desk simulator with user and admin roles, SQLite storage, ticket submission, admin review, and documentation files for a secure software engineering project. Included our original project brainstorming document in the prompt.

Summary of output: ChatGPT produced a starter Flask application with routes, templates, database models, and documentation.

### Prompt 2

> Change the app so users cannot create admin accounts. Keep only one default admin account and change the admin password to i-love-cheese.

Summary of output: ChatGPT modified registration logic so all public registrations create regular users and updated the seeded default admin password.

### Prompt 3

> Add intentional vulnerabilities for a classroom security analysis project, including CSRF, XSS, SQL injection, IDOR, and path traversal.

Summary of output: ChatGPT suggested controlled vulnerabilities and helped add them in routes/templates so another team could test the application.


## Parts Initially Not Fully Understood

- The difference between hiding admin options in the UI and enforcing role checks server-side.
- Why a GET-based delete route is a CSRF risk.
- Why rendering user input with `safe` can create stored XSS.
- Why route names and template names must match in Flask.

## AI-Generated Code That Was Changed, Rejected, or Fixed

### 1. Public Admin Registration Removed

An early version allowed users to select `admin` during registration. This was rejected because it made privilege escalation too easy and did not match the project team's desired behavior. The final version only allows one seeded admin account.

### 2. Route/Template Mismatches Fixed

Some AI-generated route names did not match template links, causing Flask `BuildError` and `TemplateNotFound` errors. The project was rebuilt so route names and template filenames are consistent.

### 3. Vulnerabilities Were Made Intentional and Documented

Some vulnerabilities were added intentionally for classroom analysis. These were documented clearly so the project remains transparent and ethical.

## Security Concerns With AI-Generated Code

AI-generated code can accidentally introduce insecure patterns, such as weak authentication, missing authorization checks, unsafe rendering, or improper file handling. In this project, some insecure patterns are intentional for security testing, but in a real application they would need to be fixed before deployment.

Furthermore, the app was made too secure in some ways for this project, we were not able to perform simple in class attacks like xss, path traversal, etc so we intentionally had to go back and add vulnerabilities.

## Limitations

- This app is not production-ready.
- It uses SQLite for simplicity.
- It intentionally contains vulnerabilities.
- It should only be run locally for educational testing.
