# MEMBER 2 — Product, Variant & Plan Management
from flask import Blueprint,request,session
from db import connect
bp=Blueprint('catalog',__name__,url_prefix='/catalog')
def allowed(): return session.get('role') in ('admin','staff')
@bp.route('/products',methods=['GET','POST'])
def products():
    if request.method=='POST':
        if not allowed(): return 'Admin/staff only',403
        try:
            name=request.form['name'].strip(); kind=request.form['product_type'].strip()
            price=float(request.form['sales_price']); cost=float(request.form['cost_price'])
            if not name or not kind or min(price,cost)<0: raise ValueError()
        except (KeyError,ValueError): return 'Invalid product input',400
        with connect() as db: db.execute('INSERT INTO products(name,product_type,sales_price,cost_price,notes) VALUES(?,?,?,?,?)',(name,kind,price,cost,request.form.get('notes','')))
        return 'Product added'
    with connect() as db: rows=db.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    return '<h2>Products</h2><ul>'+''.join(f"<li>{r['name']} | {r['product_type']} | {r['sales_price']:.2f}</li>" for r in rows)+'</ul>'
@bp.route('/plans',methods=['GET','POST'])
def plans():
    if request.method=='POST':
        if not allowed(): return 'Admin/staff only',403
        try:
            name=request.form['name'].strip(); price=float(request.form['price']); interval=request.form['billing_interval']; minimum=int(request.form.get('min_quantity',1))
            if not name or price<0 or minimum<1 or interval not in ('daily','weekly','monthly','yearly'): raise ValueError()
        except (KeyError,ValueError): return 'Invalid plan input',400
        with connect() as db: db.execute('INSERT INTO plans(name,price,billing_interval,min_quantity) VALUES(?,?,?,?)',(name,price,interval,minimum))
        return 'Plan added'
    with connect() as db: rows=db.execute('SELECT * FROM plans').fetchall()
    return '<h2>Plans</h2><ul>'+''.join(f"<li>{p['id']} {p['name']} {p['price']} / {p['billing_interval']}</li>" for p in rows)+'</ul>'
# TODO: variants CRUD, update/archive, date windows, full permission checks, tests.
