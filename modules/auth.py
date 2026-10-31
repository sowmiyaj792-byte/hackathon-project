# MEMBER 1 — Authentication & User Management
from flask import Blueprint,request,session,redirect
from werkzeug.security import generate_password_hash,check_password_hash
from db import connect
import re
bp=Blueprint('auth',__name__,url_prefix='/auth')
def strong(p):
    return len(p)>8 and bool(re.search('[A-Z]',p)) and bool(re.search('[a-z]',p)) and bool(re.search('[^A-Za-z0-9]',p))
@bp.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return "<form method='post'><input name='name' placeholder='Name' required><input name='email' type='email' required><input name='password' type='password' required><button>Sign up</button></form>"
    name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
    if not name or not email or not strong(password): return 'Invalid fields or password policy.',400
    try:
        with connect() as db: db.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',(name,email,generate_password_hash(password),'customer'))
        return 'Account created. Go to /auth/login'
    except Exception: return 'Account creation failed; email may already exist.',400
@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET': return "<form method='post'><input name='email' type='email' required><input name='password' type='password' required><button>Login</button></form>"
    with connect() as db: user=db.execute('SELECT * FROM users WHERE email=?',(request.form.get('email','').strip().lower(),)).fetchone()
    if not user or not check_password_hash(user['password_hash'],request.form.get('password','')): return 'Invalid login',401
    session.clear(); session.update(user_id=user['id'],name=user['name'],role=user['role'])
    return 'Logged in as '+user['role']
@bp.route('/logout')
def logout():
    session.clear(); return redirect('/')
# TODO: admin-only staff creation, access-control decorator, password-reset token/email, tests.
