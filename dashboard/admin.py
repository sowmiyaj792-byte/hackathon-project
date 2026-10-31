from flask import Blueprint, session, redirect, render_template_string

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/auth/login")

    if session.get("role") != "admin":
        return "Access Denied", 403

    return render_template_string("""
        <h1>Welcome Admin!</h1>
        <h2>Admin Dashboard</h2>
        <p>Manage users, staff and system activities.</p>
        <a href="/auth/logout">Logout</a>
    """)