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

#User trying to Login
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
