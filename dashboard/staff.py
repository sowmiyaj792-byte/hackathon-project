from flask import Blueprint, session, redirect, render_template_string

bp = Blueprint("staff", __name__, url_prefix="/staff")

@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/auth/login")

    if session.get("role") != "staff":
        return "Access Denied", 403

    return render_template_string("""
        <h1>Welcome Staff!</h1>
        <h2>Staff Dashboard</h2>
        <p>Manage assigned customer activities.</p>
        <a href="/auth/logout">Logout</a>
    """)