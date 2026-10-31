from flask import Blueprint, jsonify
from db import get_connection

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/summary")
def summary():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total_users FROM users")
        users = cur.fetchone()["total_users"]
        cur.execute("SELECT COUNT(*) AS total_subscriptions FROM subscriptions")
        subscriptions = cur.fetchone()["total_subscriptions"]
        cur.execute("SELECT COALESCE(SUM(amount),0) AS invoice_total FROM invoices")
        invoice_total = float(cur.fetchone()["invoice_total"])
        return jsonify(total_users=users, total_subscriptions=subscriptions,
                       invoice_total=invoice_total)
    finally:
        conn.close()
