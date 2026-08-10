from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User,Trek, Booking

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
    trek_data = []
    for trek in assigned_treks:
        # Sum up seats_booked for all active registrations
        total_registered = sum(
            b.seats_booked for b in trek.bookings if b.status != 'Cancelled'
        )
        
        trek_data.append({
            'trek': trek,
            'registered_count': total_registered
        })

    return render_template('staff/dashboard.html', trek_data=trek_data)

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

    #UPDATE status and get total available slots
    new_status=request.form.get('status','').strip()
    available_slots = request.form.get('available_slots', '').strip()
    
    #check if status is in constraints
    if new_status in ['Open','Closed','Completed']:
        trek.status=new_status
    else:
        flash('Invalid status selected.','danger')
        return redirect(url_for('staff.dashboard'))

    if available_slots:
        try:
            slots_int = int(available_slots)
            if slots_int >= 0:
                trek.available_slots = slots_int
            else:
                flash('Available slots cannot be negative.', 'danger')
                return redirect(url_for('staff.dashboard'))
        except ValueError:
            flash('Available slots must be a valid number.', 'danger')
            return redirect(url_for('staff.dashboard'))

    db.session.commit()
    flash(f'Trek: "{trek.name}" updated and Status updated to "{new_status}".', 'success') #status and available slots
    return redirect(url_for('staff.dashboard'))

# 3. VIEW PARTICIPANT LIST FOR A TREK
@staff_bp.route('/trek/<int:trek_id>/participants')
@login_required
@staff_required
def view_participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != current_user.id:
        flash('Unauthorized Access. You can only view participants for your assigned treks.', 'danger')
        return redirect(url_for('staff.dashboard'))

    active_bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status != 'Cancelled').all() #multiple seats booked by single trekker

    return render_template('staff/participants.html', trek=trek, bookings=active_bookings)

# 4.STAFF PROFILE (View Details & Edit Profile)
@staff_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@staff_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()

        if not new_username or not new_email:
            flash('Username and email fields cannot be empty.', 'danger')
            return redirect(url_for('staff.profile'))

        # Check if new username or email is already registered to another user account
        existing_user = User.query.filter(
            (User.username == new_username) | (User.email == new_email),
            User.id != current_user.id
        ).first()

        if existing_user:
            flash('That Username or Email is already in use by another account.', 'danger')
            return redirect(url_for('staff.profile'))

        current_user.username = new_username
        current_user.email = new_email
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('staff.dashboard'))

    return render_template('staff/profile.html')
