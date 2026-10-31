from flask import Flask
from db import initialize
from modules.auth import bp as auth_bp
from modules.catalog import bp as catalog_bp
from modules.subscriptions import bp as subs_bp
from modules.billing import bp as billing_bp
from modules.reports import bp as reports_bp
from dashboard.admin import bp as admin_bp
from dashboard.staff import bp as staff_bp
from dashboard.customer import bp as customer_bp
from modules.admin import bp as admin_bp
from modules.staff import bp as staff_bp
from modules.customer import bp as customer_bp
app=Flask(__name__)
app.secret_key='change-for-local-development'
for blueprint in (
    auth_bp,
    catalog_bp,
    subs_bp,
    billing_bp,
    reports_bp,
    admin_bp,
    staff_bp,
    customer_bp
):
    app.register_blueprint(blueprint)


@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Subscription Management System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #e9efff, #f8f5ff);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .welcome-box {
                background: white;
                max-width: 650px;
                width: 100%;
                padding: 55px 30px;
                border-radius: 22px;
                text-align: center;
                box-shadow: 0 12px 40px rgba(50, 60, 120, 0.12);
            }

            .logo {
                font-size: 55px;
                margin-bottom: 15px;
            }

            h1 {
                color: #263b80;
                font-size: 30px;
                margin-bottom: 15px;
            }

            h2 {
                color: #374151;
                font-size: 21px;
            }

            p {
                color: #6b7280;
                line-height: 1.7;
                margin-bottom: 30px;
            }

            .btn {
                display: inline-block;
                padding: 14px 27px;
                margin: 8px;
                border-radius: 9px;
                text-decoration: none;
                font-weight: bold;
                transition: 0.2s;
            }

            .login {
                background: #536de8;
                color: white;
            }

            .signup {
                background: #edf0ff;
                color: #354fc2;
                border: 1px solid #536de8;
            }

            .btn:hover {
                transform: translateY(-3px);
            }

            footer {
                margin-top: 35px;
                color: #9ca3af;
                font-size: 13px;
            }
        </style>
    </head>

    <body>
        <div class="welcome-box">

            <div class="logo">📊</div>

            <h1>Subscription Management System</h1>

            <h2>Welcome!</h2>

            <p>
                Manage your products, subscriptions and billing
                with one simple platform.
                <br>
                Please login or create an account to continue.
            </p>

            <a class="btn login" href="/auth/login">
                Login
            </a>

            <a class="btn signup" href="/auth/signup">
                Create an Account
            </a>

            <footer>
                Smart Subscription Management
            </footer>

        </div>
    </body>
    </html>
    """

if __name__=='__main__':
    initialize()
    app.run(debug=True)
