from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Trek, Booking

# USER / TREKKER BLUEPRINT
user_bp = Blueprint("user", __name__)

#TREKKER DECORATOR
def trekker_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        # ADDED ROLE CHECK:
        if current_user.role != 'user':
            flash('Access Denied. Trekker account required.', 'danger')
            return redirect(url_for('auth.login'))

        if current_user.is_blacklisted:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorator_function

# 2. BROWSE CATALOG WITH SEARCH & FILTER
@user_bp.route('/')
@user_bp.route('/treks')
def catalog():
    # Start with base query for open treks only
    query= Trek.query.filter_by(status='Open')

    # Read search/filter inputs from URL bar
    location_filter= request.args.get('location', '').strip()
    difficulty_filter = request.args.get('difficulty','').strip()

    # Filter by location if user typed something
    if location_filter:
        query = query.filter(Trek.location.ilike(f'%{location_filter}%'))

    # Filter by difficulty if selected
    if difficulty_filter in ['Easy', 'Moderate', 'Hard']:
        query = query.filter_by(difficulty=difficulty_filter)

    open_treks = query.all()
    return render_template('user/catalog.html', treks=open_treks)


# 3. SINGLE TREK DETAILS VIEW
@user_bp.route('/trek/<int:trek_id>')
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('user/trek_details.html', trek=trek)

#4.BOOK TREK (Includes Overbooking Prevention)
@user_bp.route('/trek/book/<int:trek_id>', methods=['POST'])
@login_required
@trekker_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # 1.Allow booking only if trek is Open
    if trek.status != 'Open':
        flash('This trek is currently closed for bookings.', 'danger')
        return redirect(url_for('user.trek_details', trek_id=trek.id))

    seats_input = request.form.get('seats_booked', '1').strip()

    try:
        requested_seats = int(seats_input)
    except ValueError:
        flash('Please enter a valid number of seats.', 'danger')
        return redirect(url_for('user.trek_details', trek_id=trek.id))

    # 2. Prevent overbooking beyond available slots
    if requested_seats <= 0:
        flash('You must book at least 1 seat.', 'danger')
        return redirect(url_for('user.trek_details', trek_id=trek.id))

    if requested_seats > trek.available_slots:
        flash(f'Cannot book "{requested_seats}" seat(s). Only "{trek.available_slots}" slots remaining.', 'danger')
        return redirect(url_for('user.trek_details', trek_id=trek.id))

    # new booking
    new_booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        seats_booked=requested_seats,
    )

    # avail slots= total-requested
    trek.available_slots -= requested_seats

    db.session.add(new_booking)
    db.session.commit()

    flash(f'Successfully booked "{requested_seats}" seat(s) for "{trek.name}".', 'success')
    return redirect(url_for('user.dashboard'))

#5. USER DASHBOARD - Active Bookings, History & Available Treks
@user_bp.route('/dashboard')
@login_required
@trekker_required
def dashboard():
    # Fetch all bookings 
    all_user_bookings= Booking.query.filter_by(user_id=current_user.id).all()

    # Separate active bookings from past/cancelled history
    active_bookings =[b for b in all_user_bookings if b.status== 'Booked'] #active
    history_bookings= [b for b in all_user_bookings if b.status in ['Completed', 'Cancelled']]#past

    # Available treks
    available_treks = Trek.query.filter_by(status='Open').all()

    return render_template(
        'user/dashboard.html',
        active_bookings=active_bookings,
        history_bookings=history_bookings,
        available_treks=available_treks
    )

#6. CANCEL BOOKING
@user_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
@trekker_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    #allow cancel of owned bookings
    if booking.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('user.dashboard'))

    if booking.status != 'Booked':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    # add slots back to trek
    #Restore slots directly via relationship
    if booking.trek:
        booking.trek.available_slots += booking.seats_booked

    booking.status = 'Cancelled'
    db.session.commit()

    flash('Booking cancelled successfully and slots restored.', 'info')
    return redirect(url_for('user.dashboard'))


# 7. EDIT PROFILE - username and email change
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@trekker_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()

        if not new_username or not new_email:
            flash('Username and email cannot be empty.', 'danger')
            return redirect(url_for('user.edit_profile'))

        # Check if username or email is already taken by another user
        existing_user = User.query.filter(
            (User.username == new_username) | (User.email == new_email),
            User.id != current_user.id
        ).first()

        if existing_user:
            flash('Username or Email is already taken by another account.', 'danger')
            return redirect(url_for('user.edit_profile'))

        current_user.username = new_username
        current_user.email = new_email
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/edit_profile.html')