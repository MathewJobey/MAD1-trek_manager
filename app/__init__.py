from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek_manager.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.staff import staff_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(user_bp, url_prefix="/user")

    return app
