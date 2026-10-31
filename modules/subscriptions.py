from flask import Blueprint, request, jsonify
from db import get_connection

subscriptions_bp = Blueprint("subscriptions", __name__)

@subscriptions_bp.post("/")
def create_subscription():
    data = request.get_json(silent=True) or {}
    required = ["user_id", "plan_id", "start_date"]
    if any(key not in data for key in required):
        return jsonify(error="user_id, plan_id and start_date are required"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO subscriptions (user_id,plan_id,start_date,end_date) VALUES (%s,%s,%s,%s)",
            (data["user_id"], data["plan_id"], data["start_date"], data.get("end_date"))
        )
        conn.commit()
        return jsonify(id=cur.lastrowid, status="active"), 201
    finally:
        conn.close()

@subscriptions_bp.get("/<int:subscription_id>")
def get_subscription(subscription_id):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM subscriptions WHERE id=%s", (subscription_id,))
        item = cur.fetchone()
        if not item:
            return jsonify(error="Subscription not found"), 404
        return jsonify(item)
    finally:
        conn.close()

@subscriptions_bp.patch("/<int:subscription_id>/cancel")
def cancel_subscription(subscription_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE subscriptions SET status='cancelled' WHERE id=%s AND status='active'",
                    (subscription_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify(error="Active subscription not found"), 404
        return jsonify(message="Subscription cancelled")
    finally:
        conn.close()
