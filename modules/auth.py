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


AUTH_STYLE = """
<style>
*{box-sizing:border-box} body{margin:0;min-height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#eaf2ff,#f6f8fc);font-family:Arial,sans-serif;color:#18243a;padding:24px}
.card{width:min(100%,420px);background:white;padding:32px;border-radius:18px;box-shadow:0 14px 45px #1e35501c}h1{margin:0 0 8px;font-size:28px}.sub{color:#68758b;margin:0 0 24px}label{display:block;font-weight:600;margin:14px 0 7px}input{width:100%;padding:12px 13px;border:1px solid #cbd5e1;border-radius:9px;font-size:15px}input:focus{outline:2px solid #b7d0ff;border-color:#2563eb}button{width:100%;margin-top:22px;padding:13px;border:0;border-radius:9px;background:#245fe8;color:white;font-size:16px;font-weight:bold;cursor:pointer}button:hover{background:#174bc2}.links{text-align:center;margin-top:20px}.links a{color:#245fe8;text-decoration:none}.hint{font-size:12px;color:#68758b;line-height:1.5}.message{padding:10px 12px;background:#fff2f0;color:#a12820;border-radius:8px;margin:12px 0}.brand{font-weight:bold;color:#245fe8;font-size:13px;margin-bottom:18px}
</style>
"""
SIGNUP_HTML = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Create account</title>""" + AUTH_STYLE + """</head><body><main class="card"><div class="brand">SUBSCRIPTION MANAGEMENT</div><h1>Create account</h1><p class="sub">Sign up to manage your subscriptions.</p>
{% for m in get_flashed_messages() %}<div class="message" role="alert">{{m}}</div>{% endfor %}
<form method="post"><label for="name">Full name</label><input id="name" name="name" autocomplete="name" placeholder="Enter your name" required>
<label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required>
<label for="password">Password</label><input id="password" name="password" type="password" autocomplete="new-password" minlength="9" placeholder="Create a strong password" required><p class="hint">Use more than 8 characters, including uppercase, lowercase and a special character.</p>
<button type="submit">Create account</button></form><div class="links">Already registered? <a href="{{url_for('auth.login')}}">Log in</a></div></main></body></html>
"""
LOGIN_HTML = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login</title>""" + AUTH_STYLE + """</head><body><main class="card"><div class="brand">SUBSCRIPTION MANAGEMENT</div><h1>Welcome back</h1><p class="sub">Log in to continue to your account.</p>
{% for m in get_flashed_messages() %}<div class="message" role="alert">{{m}}</div>{% endfor %}
<form method="post"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required>
<label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" placeholder="Enter your password" required>
<button type="submit">Log in</button></form><div class="links"><a href="{{url_for('auth.signup')}}">Create a customer account</a><p><a href="{{url_for('auth.request_password_reset')}}">Forgot password?</a></p></div></main></body></html>
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
    role = session.get("role")

    if role == "admin":
      return redirect(url_for("admin.dashboard"))

    elif role == "staff":
      return redirect(url_for("staff.dashboard"))

    elif role == "customer":
      return redirect(url_for("customer.dashboard"))

    else:
      return redirect(url_for("auth.login"))


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
