from flask import Flask
from db import initialize
from modules.auth import bp as auth_bp
from modules.catalog import bp as catalog_bp
from modules.subscriptions import bp as subs_bp
from modules.billing import bp as billing_bp
from modules.reports import bp as reports_bp
app=Flask(__name__)
app.secret_key='change-for-local-development'
for blueprint in (auth_bp,catalog_bp,subs_bp,billing_bp,reports_bp):
    app.register_blueprint(blueprint)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Subscription Management System</title>
    </head>
    <body style="font-family:Arial; margin:40px;">
        <h1>Subscription Management System</h1>
        <h3>Welcome!</h3>
        <p>Select an option below:</p>

        <p><a href="/auth/signup">Create Account / Signup</a></p>
        <p><a href="/auth/login">Login</a></p>
        <p><a href="/catalog/products">Products</a></p>
        <p><a href="/subscriptions/">Subscriptions</a></p>
        <p><a href="/billing/">Billing</a></p>
        <p><a href="/reports/">Reports</a></p>
    </body>
    </html>
    """

if __name__=='__main__':
    initialize()
    app.run(debug=True)
