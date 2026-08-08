from app.models import User, Trek, Booking
from app import db
from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_required, current_user
from functools import wraps



admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

#CUSTOM DECORATOR- to restrict users through admin routes
def admin_required(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):#takes in arguments and checks if user is 1. logged in OR 2. role=admin
        if not current_user.is_authenticated or current_user.role !='admin':
            flash('Access Denied! Admin Privileges Required.','danger')
            return redirect(url_for('auth.login'))
        return f(*args,**kwargs)
    return decorator_function

