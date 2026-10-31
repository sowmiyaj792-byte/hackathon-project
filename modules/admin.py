from flask import Blueprint, session
from modules.auth import roles_required

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/dashboard")
@roles_required("admin")
def dashboard():
    return f"""
    <h1>Admin Dashboard</h1>
    <h2>Welcome {session.get('name')}</h2>
    <p>You are logged in as Admin.</p>
    <a href="/auth/logout">Logout</a>
    """