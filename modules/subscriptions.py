# MEMBER 3 — Subscription & Quotation Management
from flask import Blueprint,request,session
from db import connect
from datetime import date
from uuid import uuid4
bp=Blueprint('subscriptions',__name__,url_prefix='/subscriptions')
@bp.route('/',methods=['GET','POST'])
def index():
    if not session.get('user_id'): return 'Login required',401
    if request.method=='POST':
        try: plan_id=int(request.form['plan_id'])
        except (KeyError,ValueError): return 'Provide valid plan_id',400
        with connect() as db:
            if not db.execute('SELECT id FROM plans WHERE id=?',(plan_id,)).fetchone(): return 'Plan not found',404
            number='SUB-'+uuid4().hex[:10].upper()
            db.execute('INSERT INTO subscriptions(subscription_number,customer_id,plan_id,start_date,status) VALUES(?,?,?,?,?)',(number,session['user_id'],plan_id,date.today().isoformat(),'Draft'))
        return 'Draft subscription created: '+number
    with connect() as db:
        if session.get('role')=='customer':
            rows=db.execute('SELECT * FROM subscriptions WHERE customer_id=?',(session['user_id'],)).fetchall()
        else: rows=db.execute('SELECT * FROM subscriptions').fetchall()
    return '<h2>Subscriptions</h2><ul>'+''.join(f"<li>{s['subscription_number']} — {s['status']}</li>" for s in rows)+'</ul><p>POST a plan_id to create a draft.</p>'
# TODO: quote templates/expiry, product lines, lifecycle transitions, renew/pause/close,
# customer record ownership enforcement and tests.
