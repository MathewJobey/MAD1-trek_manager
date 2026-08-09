from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Trek

#STAFF BLUEPRINT
staff_bp = Blueprint("staff", __name__, url_prefix='/staff')

#CUSTOM STAFF REQUIRED DECORATOR
def staff_required(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):
        #checks-1. logged in, 2.role as staff, 3. approved, 4. not blacklisted
        if not current_user.is_authenticated or current_user.role!='staff':
            flash('Access Denied. Staff Privilege required.','danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_apporved:
            flash('Account pending for approval. Please contact Admin.','warning')
            return redirect(url_for('auth.login'))
        if current_user.is_blacklisted:
            flash('Account has been deactivated. Please contact Admin.','danger')
            return redirect(url_for('auth.login'))

        return f(*args,**kwargs)
    return decorator_function
