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
        username=request.form.get('username')
        password=request.form.get('password')

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
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

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

