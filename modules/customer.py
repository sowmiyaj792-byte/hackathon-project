from flask import Blueprint, session
from modules.auth import roles_required

bp = Blueprint("customer", __name__, url_prefix="/customer")

@bp.route("/dashboard")
@roles_required("customer")
def dashboard():
    return f"""
    <h1>Customer Dashboard</h1>
    <h2>Welcome {session.get('name')}</h2>
    <p>You are logged in as Customer.</p>
    <a href="/auth/logout">Logout</a>
    """