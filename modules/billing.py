from flask import Blueprint, request, jsonify
from db import get_connection

billing_bp = Blueprint("billing", __name__)

@billing_bp.post("/invoices")
def create_invoice():
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("subscription_id", "amount")):
        return jsonify(error="subscription_id and amount are required"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO invoices (subscription_id,amount) VALUES (%s,%s)",
                    (data["subscription_id"], data["amount"]))
        conn.commit()
        return jsonify(id=cur.lastrowid, status="unpaid"), 201
    finally:
        conn.close()

@billing_bp.post("/payments")
def record_payment():
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("invoice_id", "amount")):
        return jsonify(error="invoice_id and amount are required"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (invoice_id,amount,payment_reference,status) VALUES (%s,%s,%s,'pending')",
            (data["invoice_id"], data["amount"], data.get("payment_reference"))
        )
        conn.commit()
        return jsonify(id=cur.lastrowid, status="pending",
                       message="Payment record created; no real payment was processed"), 201
    finally:
        conn.close()
