from flask import Blueprint


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return "Auth home"


@auth_bp.route("/login")
def login():
    return "Login page"


@auth_bp.route("/register")
def register():
    return "Registration page"
