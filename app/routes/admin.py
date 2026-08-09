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
@admin_bp.route('/approve-staff/<int:user_id>')
@login_required
@admin_required
def approve_staff(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    user.is_approved=True
    db.session.commit()
    flash(f'Staff: "{user.username}" approved successfully.','success')
    return redirect(url_for('admin.dashboard'))

#2. REJECT STAFF
@admin_bp.route('/reject-staff/<int:user_id>')
@login_required
@admin_required
def reject_staff(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    user.is_approved=False
    db.session.delete(user)
    db.session.commit()
    flash(f'Staff: "{user.username}" rejected and removed.','info')
    return redirect(url_for('admin.dashboard'))

#3. BLACKLIST USER
@admin_bp.route('/toggle-blacklist/<int:user_id>')
@login_required
@admin_required
def toggle_blacklist(user_id):

    #check for staff id if exists
    user=User.query.get_or_404(user_id)

    #ON AND OFF blacklist
    user.is_blacklisted=not user.is_blacklisted
    db.session.commit()
    status_str="Blacklisted" if user.is_blacklisted else "Unblacklisted"
    flash(f'User: "{user.username}" has been "{status_str}".','warning' if user.is_blacklisted else 'success')
    return redirect(url_for('admin.dashboard'))


#CRUD OPS FOR ADMIN
# 1. ADD/CREATE TREK
@admin_bp.route('/trek/add', methods=['GET','POST'])
@login_required
@admin_required
def add_trek():
    if request.method=='POST':
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', '').strip()
        duration_days = request.form.get('duration_days', '').strip()
        available_slots = request.form.get('available_slots', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        assigned_staff_id = request.form.get('assigned_staff_id')#frontend having dropdown

        if not name or not location or not difficulty or not duration_days or not available_slots:
            flash('All required trek details must be filled.','danger')
            return redirect(url_for('admin.add_trek'))

        #CREATE NEW TREK instance
        new_trek=Trek(
        name=name,
        location=location,
        difficulty=difficulty,
        duration_days=int(duration_days),
        available_slots=int(available_slots),
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None
        )

        db.session.add(new_trek)
        db.session.commit()
        flash(f'Trek: "{name}" created successfully.','success')
        return redirect(url_for('admin.dashboard'))

    #GET REQUEST- to get active&approved staff for dropdown
    approved_staff=User.query.filter_by(role='staff',is_approved=True,is_blacklisted=False).all()
    return render_template('admin/add_trek.html',staff_members=approved_staff)

#2. EDIT TREK
@admin_bp.route('/trek/edit/<int:trek_id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_trek(trek_id):
    #fetch trek
    trek=Trek.query.get_or_404(trek_id)

    if request.method=='POST':
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', '').strip() 
        duration_days = request.form.get('duration_days', '').strip()
        available_slots = request.form.get('available_slots', '').strip()
        status=request.form.get('status','').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        assigned_staff_id = request.form.get('assigned_staff_id')

        if not name or not location or not difficulty or not duration_days or not available_slots:
            flash('All required trek details must be filled.','danger')
            return redirect(url_for('admin.edit_trek',trek_id=trek.id))

        #Update trek attributes
        trek.name=name
        trek.location=location
        trek.difficulty=difficulty
        trek.duration_days=int(duration_days)
        trek.available_slots=int(available_slots)
        trek.status=status if status else 'Open'
        trek.start_date=start_date if start_date else None
        trek.end_date=end_date if end_date else None
        trek.assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None

        db.session.commit()
        flash(f'Trek: "{trek.name}" updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    # GET Request: Fetch staff list for assignment dropdown and render pre-filled form
    approved_staff = User.query.filter_by(role='staff', is_approved=True, is_blacklisted=False).all()
    return render_template('admin/edit_trek.html', trek=trek, staff_members=approved_staff)

#DELETE TREK
@admin_bp.route('/trek/delete/<int:trek_id>')
@login_required
@admin_required
def delete_trek(trek_id):
    #fetch trek
    trek = Trek.query.get_or_404(trek_id)

    # Delete from session and commit
    db.session.delete(trek)
    db.session.commit()

    flash(f'Trek: "{trek.name}" has been deleted.','info')
    return redirect(url_for('admin.dashboard'))