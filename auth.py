from functools import wraps
from flask import session, redirect, url_for, flash
from models import User

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
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def publisher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "publisher":
            flash("Publishers only!", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None