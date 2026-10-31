# MEMBER 4 — Dashboard & Reports
from flask import Blueprint,session
from db import connect
bp=Blueprint('reports',__name__,url_prefix='/reports')
@bp.route('/')
def dashboard():
    if not session.get('user_id'): return 'Login required',401
    with connect() as db:
        if session.get('role')=='customer':
            uid=session['user_id']
            active=db.execute("SELECT COUNT(*) n FROM subscriptions WHERE customer_id=? AND status='Active'",(uid,)).fetchone()['n']
            paid=db.execute('SELECT COALESCE(SUM(p.amount),0) n FROM payments p JOIN invoices i ON i.id=p.invoice_id JOIN subscriptions s ON s.id=i.subscription_id WHERE s.customer_id=?',(uid,)).fetchone()['n']
            return f'<h2>My summary</h2><p>Active: {active}</p><p>Payments: {paid:.2f}</p>'
        active=db.execute("SELECT COUNT(*) n FROM subscriptions WHERE status='Active'").fetchone()['n']
        paid=db.execute('SELECT COALESCE(SUM(amount),0) n FROM payments').fetchone()['n']
        due=db.execute("SELECT COALESCE(SUM(total),0) n FROM invoices WHERE status NOT IN ('Paid','Cancelled')").fetchone()['n']
        overdue=db.execute("SELECT COUNT(*) n FROM invoices WHERE status NOT IN ('Paid','Cancelled') AND due_date<DATE('now')").fetchone()['n']
    return f'<h2>Finance Dashboard</h2><p>Active subscriptions: {active}</p><p>Received: {paid:.2f}</p><p>Outstanding: {due:.2f}</p><p>Overdue: {overdue}</p>'
# TODO: filters, revenue charts, exports, paging, query tuning, tests.
