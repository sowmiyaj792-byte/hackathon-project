from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not all([name, email, password]):
        return jsonify(error="name, email and password are required"), 400
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s,%s,%s)",
            (name, email, generate_password_hash(password))
        )
        conn.commit()
        return jsonify(message="User registered"), 201
    except Exception:
        conn.rollback()
        return jsonify(error="Could not register user; check whether email already exists"), 400
    finally:
        conn.close()

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id,name,email,password_hash,role FROM users WHERE email=%s",
                    (data.get("email"),))
        user = cur.fetchone()
        if not user or not check_password_hash(user["password_hash"], data.get("password", "")):
            return jsonify(error="Invalid email or password"), 401
        user.pop("password_hash")
        return jsonify(message="Login successful", user=user)
    finally:
        conn.close()
