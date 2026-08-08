from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request

#AUTH blueprint
auth_bp = Blueprint("auth", __name__)

#redirect user to corresponding dashboard
def redirect_user_by_role(role):
    if role=='admin':
        return redirect(url_for('admin.dashboard'))
    elif role=='staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))

#USER LOGIN
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: #if already logged in directly redirect to the dashboard
        return redirect_user_by_role(current_user.role)

    if request.method=='POST': #after user inputs username and pass; 4 CHECKS
        username=request.form.get('username','').strip()
        password=request.form.get('password','').strip()
        #CHECK IF FIELDS ARE BLANK else leads to unnecessary db searching
        if not username or not password:
            flash('Please fill both username and password.','danger')
            return redirect(url_for('auth.login'))
        
        user=User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.','danger')
            return redirect(url_for('auth.login')) #if user not found or pass/username is incorrect

        if user.is_blacklisted:
            flash('Your account has been BLACKLISTED by Admin.','danger')
            return redirect(url_for('auth.login'))#if blacklisted by admin
    
        if user.role=='staff' and not user.is_approved:
            flash('Your staff registeration is pending for approval by Admin','warning')
            return redirect(url_for('auth.login'))#if staff not yet approved
        
        login_user(user)
        flash('Logged in successfully!', 'success')# successful login
        return redirect_user_by_role(user.role)

    return render_template('login.html')

#TREKKER REGISTERATION
@auth_bp.route('/register/user', methods=['GET','POST'])
def register_user():
    if request.method=='POST':#user types in for registering
        username=request.form.get('username','').strip()
        email=request.form.get('email','').strip()
        password=request.form.get('password','').strip()
        #CHECK IF FIELDS ARE BLANK
        if not username or not email or not password:
            flash('All fields are mandatory.','danger')
            return redirect(url_for('auth.register_user'))
        
        #USERNAME+EMAIL CHECKS

        #1. checking if username is taken
        if User.query.filter_by(username=username).first():
            flash('Username already taken.','danger')
            return redirect(url_for('auth.register_user'))

        #2. checking if email already used
        if User.query.filter_by(email=email).first():
            flash('Email already registered.','danger')
            return redirect(url_for('auth.register_user'))

        #SAVE USER TO DB
        hashed_password=generate_password_hash(password,'scrypt')
        new_user=User(username=username,email=email,password_hash=hashed_password,role='user')
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register_user.html')

#STAFF REGISTERATION
@auth_bp.route('/register/staff',methods=['GET','POST'])
def register_staff():
    if request.method=='POST':#staff tries registering
        username=request.form.get('username','').strip()
        email=request.form.get('email','').strip()
        password=request.form.get('password','').strip()
        #CHECK IF FIELDS ARE BLANK
        if not username or not email or not password:
            flash('All fields are mandatory.','danger')
            return redirect(url_for('auth.register_staff'))

        #USERNAME+EMAIL CHECKS
    
        #1. checking if username is taken
        if User.query.filter_by(username=username).first():
            flash('Username already taken.','danger')                
            return redirect(url_for('auth.register_staff'))
    
        #2. checking if email already used
        if User.query.filter_by(email=email).first():
            flash('Email already registered.','danger')
            return redirect(url_for('auth.register_staff'))

        #SAVE USER TO DB
        hashed_password=generate_password_hash(password,'scrypt')
        new_staff=User(username=username,email=email,password_hash=hashed_password,role='staff',is_approved=False) #isapproved differs for trekker nd staff
        db.session.add(new_staff)
        db.session.commit()    

        flash('Staff registeration submitted. Please wait until Admin approves...', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('register_staff.html')

#USER LOGOUT
@auth_bp.route('/logout')
@login_required #flask decorator to check if person trying to logout is actually the person logging in
def logout():
    logout_user()#encrypted session cookie gets erased for that session and flask goes to anonymoususermixin 
    flash('You have been logged out successfully.','info')
    return redirect(url_for('auth.login'))