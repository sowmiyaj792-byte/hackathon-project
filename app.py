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
    return '<h1>Subscription Management System</h1><p>Visit /auth/signup, /auth/login, /catalog/products, /subscriptions/, /billing/, /reports/</p>'
if __name__=='__main__':
    initialize()
    app.run(debug=True)
