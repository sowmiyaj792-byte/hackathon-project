from datetime import date

import mysql.connector
from flask import Blueprint, jsonify, request

from db import get_connection

subscriptions_bp = Blueprint("subscriptions", __name__)


def _positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _parse_date(value, field_name):
    if not isinstance(value, str):
        return None, f"{field_name} must use YYYY-MM-DD format"
    try:
        parsed = date.fromisoformat(value)
        return parsed, None
    except ValueError:
        return None, f"{field_name} must be a valid YYYY-MM-DD date"


def _serialize(item):
    for field in ("start_date", "end_date"):
        if item.get(field) is not None:
            item[field] = item[field].isoformat()
    return item


@subscriptions_bp.post("/")
def create_subscription():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400

    for field in ("user_id", "plan_id"):
        if not _positive_integer(data.get(field)):
            return jsonify(error=f"{field} must be a positive integer"), 400

    start_date, error = _parse_date(data.get("start_date"), "start_date")
    if error:
        return jsonify(error=error), 400

    end_date = None
    if data.get("end_date") is not None:
        end_date, error = _parse_date(data["end_date"], "end_date")
        if error:
            return jsonify(error=error), 400
        if end_date <= start_date:
            return jsonify(error="end_date must be later than start_date"), 400

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE id=%s", (data["user_id"],))
        if cur.fetchone() is None:
            return jsonify(error="User not found"), 404

        cur.execute("SELECT id FROM plans WHERE id=%s", (data["plan_id"],))
        if cur.fetchone() is None:
            return jsonify(error="Plan not found"), 404

        cur.execute(
            "INSERT INTO subscriptions "
            "(user_id, plan_id, start_date, end_date) VALUES (%s, %s, %s, %s)",
            (data["user_id"], data["plan_id"], start_date, end_date),
        )
        conn.commit()
        return jsonify(id=cur.lastrowid, status="active"), 201

    except mysql.connector.Error:
        if conn:
            conn.rollback()
        return jsonify(error="Database error while creating subscription"), 500

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


@subscriptions_bp.get("/")
def list_subscriptions():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM subscriptions ORDER BY id DESC")
        return jsonify([_serialize(item) for item in cur.fetchall()])
    except mysql.connector.Error:
        return jsonify(error="Database error while listing subscriptions"), 500
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


@subscriptions_bp.get("/<int:subscription_id>")
def get_subscription(subscription_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM subscriptions WHERE id=%s",
            (subscription_id,),
        )
        item = cur.fetchone()

        if item is None:
            return jsonify(error="Subscription not found"), 404

        return jsonify(_serialize(item))

    except mysql.connector.Error:
        return jsonify(error="Database error while getting subscription"), 500
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


@subscriptions_bp.patch("/<int:subscription_id>/cancel")
def cancel_subscription(subscription_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE subscriptions SET status='cancelled' "
            "WHERE id=%s AND status='active'",
            (subscription_id,),
        )

        if cur.rowcount == 0:
            conn.rollback()
            return jsonify(error="Active subscription not found"), 404

        conn.commit()
        return jsonify(message="Subscription cancelled", status="cancelled")

    except mysql.connector.Error:
        if conn:
            conn.rollback()
        return jsonify(error="Database error while cancelling subscription"), 500
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


@subscriptions_bp.patch("/<int:subscription_id>/activate")
def activate_subscription(subscription_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE subscriptions SET status='active' "
            "WHERE id=%s AND status='cancelled' "
            "AND (end_date IS NULL OR end_date >= CURDATE())",
            (subscription_id,),
        )

        if cur.rowcount == 0:
            conn.rollback()
            return jsonify(error="Subscription cannot be activated"), 409

        conn.commit()
        return jsonify(message="Subscription activated", status="active")

    except mysql.connector.Error:
        if conn:
            conn.rollback()
        return jsonify(error="Database error while activating subscription"), 500
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()


@subscriptions_bp.patch("/<int:subscription_id>/renew")
def renew_subscription(subscription_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400

    start_date, error = _parse_date(data.get("start_date"), "start_date")
    if error:
        return jsonify(error=error), 400

    end_date, error = _parse_date(data.get("end_date"), "end_date")
    if error:
        return jsonify(error=error), 400

    if end_date <= start_date:
        return jsonify(error="end_date must be later than start_date"), 400

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE subscriptions SET start_date=%s, end_date=%s, status='active' "
            "WHERE id=%s",
            (start_date, end_date, subscription_id),
        )

        if cur.rowcount == 0:
            cur.execute(
                "SELECT id FROM subscriptions WHERE id=%s",
                (subscription_id,),
            )
            if cur.fetchone() is None:
                return jsonify(error="Subscription not found"), 404

        conn.commit()
        return jsonify(
            message="Subscription renewed",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            status="active",
        )

    except mysql.connector.Error:
        if conn:
            conn.rollback()
        return jsonify(error="Database error while renewing subscription"), 500
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()