# MEMBER 4 — Billing & Payments
from flask import Blueprint,request,session
from db import connect
from datetime import date
bp=Blueprint('billing',__name__,url_prefix='/billing')
@bp.route('/')
def invoices():
    if not session.get('user_id'): return 'Login required',401
    with connect() as db:
        if session.get('role')=='customer':
            rows=db.execute('SELECT i.* FROM invoices i JOIN subscriptions s ON s.id=i.subscription_id WHERE s.customer_id=?',(session['user_id'],)).fetchall()
        else: rows=db.execute('SELECT * FROM invoices').fetchall()
    return '<h2>Invoices</h2><ul>'+''.join(f"<li>{i['invoice_number']} | {i['total']:.2f} | {i['status']}</li>" for i in rows)+'</ul>'
@bp.route('/payments',methods=['POST'])
def payment():
    if session.get('role') not in ('admin','staff'): return 'Admin/staff only',403
    try:
        invoice_id=int(request.form['invoice_id']); amount=float(request.form['amount']); method=request.form['method'].strip()
        if amount<=0 or not method: raise ValueError()
    except (KeyError,ValueError): return 'Invalid payment values',400
    with connect() as db:
        inv=db.execute('SELECT * FROM invoices WHERE id=?',(invoice_id,)).fetchone()
        if not inv or inv['status'] in ('Paid','Cancelled'): return 'Invoice not payable',400
        received=db.execute('SELECT COALESCE(SUM(amount),0) n FROM payments WHERE invoice_id=?',(invoice_id,)).fetchone()['n']
        if received+amount>inv['total']+0.00001: return 'Amount exceeds remaining balance',400
        db.execute('INSERT INTO payments(invoice_id,method,amount,payment_date) VALUES(?,?,?,?)',(invoice_id,method,amount,date.today().isoformat()))
        if received+amount>=inv['total']-0.00001: db.execute("UPDATE invoices SET status='Paid' WHERE id=?",(invoice_id,))
    return 'Payment saved'
# TODO: idempotent recurring invoice generator, tax/discount policy, due dates, confirm/cancel,
# invoice printing, overdue queues, transaction tests.
