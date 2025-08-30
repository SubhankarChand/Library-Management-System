from functools import wraps
from flask import session, redirect, url_for, flash
from extensions import db
from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route('/login')
def login():
    # Your login logic
    pass
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admins only!", "danger")
            return redirect(url_for("index"))  # Changed from "home" to "index"
        return f(*args, **kwargs)
    return decorated_function

def publisher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "publisher":
            flash("Publishers only!", "danger")
            return redirect(url_for("index"))  # Changed from "home" to "index"
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if "user_id" in session:
        # Import here to avoid circular imports
        from models import User
        return User.query.get(session["user_id"])
    return None