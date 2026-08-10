from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

#starting up the extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    
    app.config['SECRET_KEY'] = 'trek-management-secret-key-2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek_management.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    #BIND
    db.init_app(app)
    login_manager.init_app(app)

    #LOGIN SETTINGS
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    #import + Register BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.staff import staff_bp
    from app.routes.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)

    # DATABASE INITIALIZATION AND ADMIN SEEDING
    with app.app_context():
        from app.models import User, Trek, Booking  # Load models into SQLAlchemy
        db.create_all()

        # Check if an Admin account already exists
        admin_account = User.query.filter_by(role='admin').first()
        
        # Create an admin account if it's not there
        if not admin_account:
            hashed_password = generate_password_hash('admin123', method='scrypt')
            default_admin = User(
                username='admin',
                email='admin@trek.com',
                password_hash=hashed_password,
                role='admin',
                is_approved=True,
                is_blacklisted=False
            )
            db.session.add(default_admin)
            db.session.commit()

    return app
