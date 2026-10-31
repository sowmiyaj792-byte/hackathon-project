from flask import Blueprint, session, redirect, render_template_string

bp = Blueprint("customer", __name__, url_prefix="/customer")

@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/auth/login")

    if session.get("role") != "customer":
        return "Access Denied", 403

    return render_template_string("""
        <h1>Welcome Customer!</h1>
        <h2>Customer Dashboard</h2>
        <p>View products and manage your subscriptions.</p>
        <a href="/auth/logout">Logout</a>
    """)