from datetime import datetime
from flask_login import UserMixin #provides some login features
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): # uses 1. is_authenticated, 2. is_active, 3. is_anonymous, 4. get_id() for user LOGIN & session tracking
    __tablename__="users" #USERS TABLE

    id= db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(128), nullable=False) #store hashed password of user
    role= db.Column(db.String(20), nullable=False, default='user')
    is_approved= db.Column(db.Boolean, default=True)
    is_blacklisted= db.Column(db.Boolean, default=False)

    bookings= db.relationship('Booking', backref='trekker', lazy=True) # a way to get all the bookings of a user. user.bookings will list it and reverse if booking is b then b.trekker shows u the user.
    assigned_treks= db.relationship('Trek', backref='assigned_staff', lazy=True)# staff_user.assigned_treks will give it | let say trek t object then t.assigned_staff gives USER object of the staff member who is managing that trek.

class Trek(db.Model):
    __tablename__ = "treks" #TREKS TABLE

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100), nullable=False)
    location= db.Column(db.String(100), nullable=False)
    difficulty= db.Column(db.String(20), nullable=False)
    duration_days= db.Column(db.Integer, nullable=False)
    available_slots= db.Column(db.Integer, nullable=False)
    status= db.Column(db.String(20), nullable=False, default='Open')
    start_date = db.Column(db.String(20), nullable=True)
    end_date= db.Column(db.String(20), nullable=True)

    # Foreign Key linking to the Trek Staff member assigned to lead this trek
    assigned_staff_id= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)#can be null as so a trek can be created first and later a staff cna be assigned
    bookings = db.relationship('Booking', backref='trek', lazy=True)#for any booking obj b, b.trek= full details of that booked trek

    # DB check Constraints for DIFFICULTY, STATUS
    __table_args__ = (
        db.CheckConstraint(
            "difficulty IN ('Easy', 'Moderate', 'Hard')", 
            name="check_trek_difficulty"
        ),
        db.CheckConstraint(
            "status IN ('Pending', 'Approved', 'Open', 'Closed', 'Completed')", 
            name="check_trek_status"
        ),
    )

class Booking(db.Model):
    __tablename__ = 'bookings' #BOOKING TABLE

    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id= db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date= db.Column(db.DateTime, default=datetime.utcnow)
    status= db.Column(db.String(20), nullable=False, default='Booked')

    # DB check constraints for STATUS
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('Booked', 'Cancelled', 'Completed')", 
            name="check_booking_status"
        ),
    )