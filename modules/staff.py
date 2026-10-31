from flask import Blueprint, session
from modules.auth import roles_required

bp = Blueprint("staff", __name__, url_prefix="/staff")

@bp.route("/dashboard")
@roles_required("staff")
def dashboard():
    return f"""
    <h1>Staff Dashboard</h1>
    <h2>Welcome {session.get('name')}</h2>
    <p>You are logged in as Staff.</p>
    <a href="/auth/logout">Logout</a>
    """