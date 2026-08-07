from datetime import datetime
from flask_login import UserMixin #provides some login features
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
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