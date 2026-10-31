"""Member 1: Authentication and User Management.

Blueprint prefix: /auth
Shared database contract: users(id, name, email, password_hash, role)
Roles: admin, staff, customer
"""
from functools import wraps
import re
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, flash, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import connect

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Starter in-memory reset tokens are intentionally NOT production-ready.
# Use a persistent, hashed, expiring token store and email provider for deployment.
_RESET_TOKENS = {}


def strong_password(password: str) -> bool:
    """Project policy: >8 chars, uppercase, lowercase, special character."""
    return (
        len(password) > 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"[^A-Za-z0-9]", password))
    )


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    with connect() as db:
        return db.execute(
            "SELECT id, name, email, role FROM users WHERE id=?", (uid,)
        ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                return "Forbidden: insufficient role permissions.", 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


SIGNUP_HTML = """
<h1>Customer Signup</h1>
{% for m in get_flashed_messages() %}<p>{{m}}</p>{% endfor %}
<form method="post">
<label>Full name</label><input name="name" required>
<label>Email</label><input name="email" type="email" required>
<label>Password</label><input name="password" type="password" required>
<p>Password: more than 8 characters, uppercase, lowercase, special character.</p>
<button>Create account</button></form>
<a href="{{url_for('auth.login')}}">Login</a>
"""
LOGIN_HTML = """
<h1>Login</h1>
{% for m in get_flashed_messages() %}<p>{{m}}</p>{% endfor %}
<form method="post">
<label>Email</label><input name="email" type="email" required>
<label>Password</label><input name="password" type="password" required>
<button>Login</button></form>
<a href="{{url_for('auth.signup')}}">Create customer account</a>
<p><a href="{{url_for('auth.request_password_reset')}}">Forgot password?</a></p>
"""
STAFF_HTML = """
<h1>Create Staff Account</h1>
{% for m in get_flashed_messages() %}<p>{{m}}</p>{% endfor %}
<form method="post">
<label>Name</label><input name="name" required>
<label>Email</label><input name="email" type="email" required>
<label>Temporary password</label><input name="password" type="password" required>
<button>Create staff member</button></form>
"""


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template_string(SIGNUP_HTML)
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not name or not email or not strong_password(password):
        flash("Please enter a name, valid email, and password matching the policy.")
        return render_template_string(SIGNUP_HTML), 400
    try:
        with connect() as db:
            db.execute(
                "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), "customer"),
            )
    except Exception:
        # Avoid exposing database details to users.
        flash("Account could not be created. The email may already be registered.")
        return render_template_string(SIGNUP_HTML), 400
    flash("Account created. Please log in.")
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        flash("Incorrect email or password.")
        return render_template_string(LOGIN_HTML), 401
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return redirect(url_for("auth.profile"))


@bp.route("/profile")
@login_required
def profile():
    user = current_user()
    return (
        f"<h1>Welcome, {user['name']}</h1>"
        f"<p>Account role: {user['role']}</p>"
        "<p><a href='/auth/logout'>Logout</a></p>"
    )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/staff/create", methods=["GET", "POST"])
@roles_required("admin")
def create_staff():
    """Only an authenticated admin can create staff users."""
    if request.method == "GET":
        return render_template_string(STAFF_HTML)
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not name or not email or not strong_password(password):
        flash("Invalid details or password policy.")
        return render_template_string(STAFF_HTML), 400
    try:
        with connect() as db:
            db.execute(
                "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), "staff"),
            )
    except Exception:
        flash("Could not create staff account. Email may already exist.")
        return render_template_string(STAFF_HTML), 400
    flash("Staff account created.")
    return redirect(url_for("auth.profile"))


@bp.route("/password-reset", methods=["GET", "POST"])
def request_password_reset():
    """Demo flow only: does not send email. Configure mail delivery before use."""
    if request.method == "GET":
        return """<h1>Password reset</h1><form method='post'>
        <input name='email' type='email' required placeholder='Registered email'>
        <button>Request reset</button></form>"""
    email = request.form.get("email", "").strip().lower()
    with connect() as db:
        user = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    # Same response for known/unknown addresses to reduce account enumeration.
    if user:
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(minutes=20)
        _RESET_TOKENS[token] = {"user_id": user["id"], "expires": expires}
        # DEVELOPMENT ONLY: expose token in server logs, never in production.
        current_app.logger.warning("DEV password reset token for %s: %s", email, token)
    return ("If the account exists, reset instructions will be sent. "
            "Email sending is not configured in this starter.")


@bp.route("/password-reset/confirm", methods=["GET", "POST"])
def confirm_password_reset():
    if request.method == "GET":
        return """<h1>Set a new password</h1><form method='post'>
        <input name='token' required placeholder='Reset token'>
        <input name='password' type='password' required placeholder='New password'>
        <button>Change password</button></form>"""
    token = request.form.get("token", "")
    password = request.form.get("password", "")
    item = _RESET_TOKENS.get(token)
    if not item or item["expires"] < datetime.now(timezone.utc):
        _RESET_TOKENS.pop(token, None)
        return "Reset token is invalid or expired.", 400
    if not strong_password(password):
        return "Password does not meet the required policy.", 400
    with connect() as db:
        db.execute("UPDATE users SET password_hash=? WHERE id=?",
                   (generate_password_hash(password), item["user_id"]))
    _RESET_TOKENS.pop(token, None)
    return "Password updated. Please log in."


# For app integration, register this blueprint in app.py:
# from modules.auth import bp as auth_bp
# app.register_blueprint(auth_bp)
