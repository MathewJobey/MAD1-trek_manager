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
        if not current_user.is_approved:
            flash('Account pending for approval. Please contact Admin.','warning')
            return redirect(url_for('auth.login'))
        if current_user.is_blacklisted:
            flash('Account has been deactivated. Please contact Admin.','danger')
            return redirect(url_for('auth.login'))

        return f(*args,**kwargs)
    return decorator_function

#STAFF DASHBOARD
@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():

    #show treks assigned for the staff
    assigned_treks=Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    return render_template('staff/dashboard.html',treks=assigned_treks)

#EDIT TREK STATUS
@staff_bp.route('/trek/status/<int:trek_id>',methods=['POST'])
@login_required
@staff_required
def update_status(trek_id):
    #check if trek exist
    trek=Trek.query.get_or_404(trek_id)

    #SECURITY check to make sure the staff is editing ONLY the trek thats assigned to them
    if trek.assigned_staff_id!=current_user.id:
        flash('Unauthorized Access. You can only edit treks that are assigned to you.','danger')
        return redirect(url_for('staff.dashboard'))

    #UPDATE status
    new_status=request.form.get('status','').strip()
    #check if status is in constraints
    if new_status in ['Open','Closed','Completed']:
        trek.status=new_status
        db.session.commit()
        flash(f'Status for Trek: "{trek.name}" updated to "{new_status}".', 'success')
    else:
        flash('Invalid status selected.','danger')

    return redirect(url_for('staff.dashboard'))
