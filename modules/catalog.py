from flask import Blueprint, request, jsonify
from db import get_connection

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.get("/products")
def list_products():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        return jsonify(cur.fetchall())
    finally:
        conn.close()

@catalog_bp.post("/products")
def add_product():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return jsonify(error="Product name is required"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, description) VALUES (%s,%s)",
                    (data["name"], data.get("description")))
        conn.commit()
        return jsonify(id=cur.lastrowid, message="Product added"), 201
    finally:
        conn.close()

@catalog_bp.post("/plans")
def add_plan():
    data = request.get_json(silent=True) or {}
    required = ["product_id", "name", "price", "billing_interval"]
    if any(key not in data for key in required):
        return jsonify(error="product_id, name, price and billing_interval are required"), 400
    if data["billing_interval"] not in ("monthly", "yearly"):
        return jsonify(error="billing_interval must be monthly or yearly"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO plans (product_id,name,price,billing_interval) VALUES (%s,%s,%s,%s)",
            (data["product_id"], data["name"], data["price"], data["billing_interval"])
        )
        conn.commit()
        return jsonify(id=cur.lastrowid, message="Plan added"), 201
    finally:
        conn.close()
