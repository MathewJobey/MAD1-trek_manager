from app.models import User, Trek, Booking
from app import db
from flask import Blueprint,render_template,redirect,url_for,flash,request
from flask_login import login_required, current_user
from functools import wraps



admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

#CUSTOM DECORATOR- to restrict users through admin routes like how login_required deco already exists
def admin_required(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):#takes in arguments and checks if user is 1. logged in OR 2. role=admin
        if not current_user.is_authenticated or current_user.role !='admin':
            flash('Access Denied! Admin Privileges Required.','danger')
            return redirect(url_for('auth.login'))
        return f(*args,**kwargs)
    return decorator_function

#ADMIN DASHBOARD
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():

    #getting values from DB to send to FRONTEND {1.pending approval, 2. all users, 3. all treks, 4. all bookings}
    pending_staff=User.query.filter_by(role='staff',is_approved=False).all()
    all_users=User.query.filter(User.role!='admin').all() #all except the admin
    all_treks=Trek.query.all()
    all_bookings=Booking.query.all()

    return render_template('admin/dashboard.html', pending_staff=pending_staff,users=all_users,treks=all_treks,bookings=all_bookings)

