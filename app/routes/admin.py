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

#1. APPROVE STAFF
@admin_bp.route('/approve-staff/<int: user_id>')
@login_required
@admin_required
def approve_staff(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    user.is_approved=True
    db.session.commit()
    flash(f'Staff: {user.username} approved successfully.','success')
    return redirect(url_for('admin.dashboard'))

#2. REJECT STAFF
@admin_bp.route('/reject-staff/<int: user_id>')
@login_required
@admin_required
def reject_staff(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    user.is_approved=False
    db.session.commit()
    flash(f'Staff: {user.username} rejected and removed.','info')
    return redirect(url_for('admin.dashboard'))

#3. BLACKLIST USER
@admin_bp.route('/toggle-blacklist/<int: user_id>')
@login_required
@admin_required
def toggle_blacklist(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    #ON AND OFF blacklist
    user.is_blacklisted=not user.is_blacklisted
    db.session.commit()

    flash(f'User: {user.username} has been {user.status}.','warning' if user.is_blacklisted else 'success')
    return redirect(url_for('admin.dashboard'))


