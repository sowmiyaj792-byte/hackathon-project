from flask import Flask, jsonify
from modules.auth import auth_bp
from modules.catalog import catalog_bp
from modules.subscriptions import subscriptions_bp
from modules.billing import billing_bp
from modules.reports import reports_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "local-development-only-change-me"

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(catalog_bp, url_prefix="/catalog")
app.register_blueprint(subscriptions_bp, url_prefix="/subscriptions")
app.register_blueprint(billing_bp, url_prefix="/billing")
app.register_blueprint(reports_bp, url_prefix="/reports")

@app.get("/")
def home():
    return jsonify({
        "message": "Subscription Management System API is running",
        "modules": ["auth", "catalog", "subscriptions", "billing", "reports"]
    })

if __name__ == "__main__":
    app.run(debug=True)
