import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "helpdesk.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-for-class-project"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(DB_PATH)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    tickets = db.relationship("Ticket", backref="owner", lazy=True)

    @property
    def is_admin(self):
        return self.role == "admin"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(30), nullable=False, default="Open")
    response = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return route_function(*args, **kwargs)
    return wrapper


def seed_database():
    db.create_all()
    admin = User.query.filter_by(username="admin").first()
    if admin is None:
        admin = User(username="admin", role="admin")
        admin.set_password("i-love-cheese")
        db.session.add(admin)
        db.session.commit()


@app.before_request
def initialize_database():
    seed_database()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    errors = []
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already exists.")

        if not errors:
            # SECURITY FIX REQUESTED BY PROJECT TEAM:
            # Registration always creates a regular user. The only admin is seeded by the app.
            user = User(username=username, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", errors=errors, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_panel" if current_user.is_admin else "dashboard"))

    errors = []
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # INTENTIONAL VULNERABILITY: SQL Injection
        # This query concatenates user input directly into SQL.
        # Example classroom test username: ' OR '1'='1' --
        raw_sql = f"SELECT id FROM user WHERE username = '{username}'"
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            row = cursor.execute(raw_sql).fetchone()
        except sqlite3.Error:
            row = None
        finally:
            connection.close()

        user = User.query.get(row[0]) if row else None

        # The password check is intentionally bypassed when an injection-like payload is used,
        # making SQL injection demonstrable in a small class app.
        if user and (user.check_password(password) or "'" in username or "--" in username):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin_panel" if user.is_admin else "dashboard"))

        errors.append("Invalid username or password.")

    return render_template("login.html", errors=errors)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin_panel"))
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.id.desc()).all()
    return render_template("dashboard.html", tickets=tickets)


@app.route("/create-ticket", methods=["GET", "POST"])
@login_required
def create_ticket():
    if current_user.is_admin:
        return redirect(url_for("admin_panel"))

    errors = []
    title = ""
    description = ""
    priority = "Medium"

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium").strip()
        uploaded_file = request.files.get("attachment")
        saved_filename = None

        if not title:
            errors.append("Title is required.")
        if not description:
            errors.append("Description is required.")
        if priority not in ["Low", "Medium", "High"]:
            errors.append("Invalid priority.")

        if uploaded_file and uploaded_file.filename:
            # INTENTIONAL WEAKNESS: filename is not sanitized.
            # This supports path-traversal-style file handling analysis.
            saved_filename = uploaded_file.filename
            uploaded_file.save(UPLOAD_DIR / saved_filename)

        if not errors:
            ticket = Ticket(
                title=title,
                description=description,
                priority=priority,
                attachment=saved_filename,
                user_id=current_user.id,
            )
            db.session.add(ticket)
            db.session.commit()
            flash("Ticket submitted.", "success")
            return redirect(url_for("dashboard"))

    return render_template("create_ticket.html", errors=errors, title=title, description=description, priority=priority)


@app.route("/ticket/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    # INTENTIONAL VULNERABILITY: IDOR / Broken Access Control
    # No owner check is performed, so users can view other users' tickets by changing the ID.
    return render_template("ticket_detail.html", ticket=ticket)


@app.route("/download")
@login_required
def download_file():
    filename = request.args.get("file", "")
    # INTENTIONAL VULNERABILITY: Path Traversal
    # The file path is built directly from user-controlled input.
    requested_path = UPLOAD_DIR / filename
    if not requested_path.exists():
        abort(404)
    return send_file(requested_path, as_attachment=True)


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return render_template("admin_panel.html", tickets=tickets)


@app.route("/admin/ticket/<int:ticket_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    errors = []

    if request.method == "POST":
        status = request.form.get("status", "").strip()
        response = request.form.get("response", "").strip()
        if status not in ["Open", "In Progress", "Closed"]:
            errors.append("Invalid status.")
        if not errors:
            ticket.status = status
            ticket.response = response
            db.session.commit()
            flash("Ticket updated.", "success")
            return redirect(url_for("admin_panel"))

    return render_template("admin_ticket_detail.html", ticket=ticket, errors=errors)


@app.route("/delete_ticket/<int:ticket_id>")
@login_required
@admin_required
def delete_ticket(ticket_id):
    # INTENTIONAL VULNERABILITY: CSRF
    # This destructive action uses GET and has no CSRF token.
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash("Ticket deleted.", "success")
    return redirect(url_for("admin_panel"))


@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", error_code=403, message="Forbidden"), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error_code=404, message="Not found"), 404


if __name__ == "__main__":
    app.run(debug=True)
