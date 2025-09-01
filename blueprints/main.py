import os
import re
from datetime import datetime, timedelta
from flask import (Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from .auth import login_required, admin_required, publisher_required, get_current_user
from models import User, Book, Category, Borrowing, Review

main_bp = Blueprint("main", __name__)

def allowed_file(filename, allowed_extensions):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

#==============================================================================
# CORE & AUTHENTICATION ROUTES
#==============================================================================

@main_bp.route("/")
def index():
    """
    Serves the welcome page for logged-out users and the book catalog
    for logged-in users.
    """
    user = get_current_user()
    if not user:
        return render_template("home.html", current_user=None)

    # If user is logged in, show them the book catalog with filters
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    selected_category = request.args.get('category', '')
    selected_genre = request.args.get('genre', '')
    selected_book_type = request.args.get('book_type', '')
    selected_status = request.args.get('status', '')

    query = Book.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(db.or_(Book.title.ilike(search_term), Book.author.ilike(search_term)))
    if selected_category:
        query = query.filter_by(category=selected_category)
    if selected_genre:
        query = query.filter_by(genre=selected_genre)
    if selected_book_type:
        query = query.filter_by(book_type=selected_book_type)
    if selected_status == 'available':
        query = query.filter(Book.available_copies > 0)

    books_pagination = query.order_by(Book.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    categories = [cat[0] for cat in db.session.query(Book.category).distinct().all() if cat[0]]
    genres = [g[0] for g in db.session.query(Book.genre).distinct().all() if g[0]]
    book_types = [bt[0] for bt in db.session.query(Book.book_type).distinct().all() if bt[0]]

    return render_template(
        "index.html",
        current_user=user, books=books_pagination, search=search_query,
        categories=categories, genres=genres, book_types=book_types,
        selected_category=selected_category, selected_genre=selected_genre,
        selected_book_type=selected_book_type, selected_status=selected_status,
    )

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if not username or len(username.strip()) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template("register.html", form_data=request.form)
        if User.query.filter_by(username=username).first():
            flash("That username is already taken. Please choose another.", "danger")
            return render_template("register.html", form_data=request.form)
        
        if not email or not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html", form_data=request.form)
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("register.html", form_data=request.form)

        if not password or len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html", form_data=request.form)
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", form_data=request.form)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in to continue.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username}!", "success")

            # --- CORRECTED REDIRECTION LOGIC ---
            if user.role == "admin":
                return redirect(url_for("main.admin_dashboard"))
            elif user.role == "publisher":
                return redirect(url_for("main.publisher_dashboard"))
            else: # This handles the 'user' role
                return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")
    
    return render_template("login.html")

@main_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("main.index"))

#==============================================================================
# DASHBOARD ROUTES
#==============================================================================

@main_bp.route("/user/dashboard")
@login_required
def user_dashboard():
    # Regular users are redirected to the main catalog page
    return redirect(url_for('main.index'))

@main_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "total_books": Book.query.count(),
        "total_users": User.query.filter(User.role != 'admin').count(),
        "total_publishers": User.query.filter_by(role="publisher").count(),
        "total_borrowed": Borrowing.query.filter_by(is_returned=False).count()
    }
    return render_template("admin_dashboard.html", current_user=get_current_user(), **stats)

# In main.py

@main_bp.route("/publisher/dashboard")
@publisher_required
def publisher_dashboard():
    user = get_current_user()
    
    # ✅ FIXED: Query for the books published by this user
    published_books = Book.query.filter_by(publisher_id=user.id).order_by(Book.created_at.desc()).all()

    # Basic stats
    published_books_count = len(published_books)
    available_copies = db.session.query(db.func.sum(Book.available_copies)).filter(Book.publisher_id == user.id).scalar() or 0
    
    # Query for borrows of this publisher's books
    borrows_query = Borrowing.query.join(Book).filter(Book.publisher_id == user.id)
    borrowed_count = borrows_query.count()
    
    # Average rating calculation
    avg_rating = db.session.query(db.func.avg(Review.rating)).join(Book).filter(Book.publisher_id == user.id).scalar() or 0
    
    return render_template(
        "publisher_dashboard.html",
        current_user=user,
        books=published_books, 
        published_books_count=published_books_count, 
        borrowed_count=borrowed_count,
        available_copies=int(available_copies),
        average_rating=float(avg_rating if avg_rating else 0)
    )

#==============================================================================
# ADMIN MANAGEMENT ROUTES
#==============================================================================

@main_bp.route("/admin/manage-users")
@admin_required
def manage_users():
    # Query all users except the currently logged-in admin to prevent self-actions
    current_admin_id = get_current_user().id
    users = User.query.filter(User.id != current_admin_id).order_by(User.created_at.desc()).all()
    return render_template("manage_users.html", users=users, current_user=get_current_user())

@main_bp.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    
    if user_to_delete.role == 'admin':
        flash("Admins cannot be deleted.", "danger")
        return redirect(url_for('main.manage_users'))
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f"User '{user_to_delete.username}' has been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {e}", "danger")

    return redirect(url_for('main.manage_users'))

#==============================================================================
# BOOK MANAGEMENT ROUTES (FOR PUBLISHERS/ADMINS)
#==============================================================================

@main_bp.route("/add-book", methods=['GET', 'POST'])
@publisher_required
def add_book():
    if request.method == 'POST':
        cover_image = request.files.get('cover_image')
        pdf_file = request.files.get('pdf_file')
        cover_filename, pdf_filename = None, None

        if cover_image and allowed_file(cover_image.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
            cover_filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(current_app.config['BOOK_COVER_FOLDER'], cover_filename))

        if pdf_file and allowed_file(pdf_file.filename, current_app.config['ALLOWED_PDF_EXTENSIONS']):
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(current_app.config['BOOK_PDF_FOLDER'], pdf_filename))

        total_copies = int(request.form.get('total_copies', 1))
        new_book = Book(
            title=request.form.get('title'), author=request.form.get('author'),
            description=request.form.get('description'), category=request.form.get('category'),
            genre=request.form.get('genre'), total_copies=total_copies,
            available_copies=total_copies, publication_year=int(request.form.get('publication_year')),
            isbn=request.form.get('isbn'), publisher_id=get_current_user().id,
            cover_image=cover_filename, pdf_file=pdf_filename
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('main.publisher_dashboard'))
    return render_template('book_form.html', current_user=get_current_user())

@main_bp.route("/edit-book/<int:book_id>", methods=['GET', 'POST'])
@publisher_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.publisher_id != get_current_user().id:
        flash("You are not authorized to edit this book.", "danger")
        return redirect(url_for('main.publisher_dashboard'))
    
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        # ... (full update logic would go here)
        db.session.commit()
        flash(f"'{book.title}' has been successfully updated.", "success")
        return redirect(url_for('main.publisher_dashboard'))
    return render_template('edit_book.html', book=book, current_user=get_current_user())

@main_bp.route("/delete-book/<int:book_id>", methods=['POST'])
@publisher_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.publisher_id != get_current_user().id:
        flash("You are not authorized to delete this book.", "danger")
        return redirect(url_for('main.publisher_dashboard'))
    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' has been successfully deleted.", "success")
    return redirect(url_for('main.publisher_dashboard'))

#==============================================================================
# USER ACTION ROUTES
#==============================================================================

@main_bp.route("/book/<int:book_id>")
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
    
    # Calculate average rating
    if reviews:
        average_rating = sum(r.rating for r in reviews) / len(reviews)
    else:
        average_rating = 0
        
    return render_template(
        "book_detail.html", 
        book=book, 
        reviews=reviews,
        average_rating=average_rating,
        current_user=get_current_user()
    )

@main_bp.route("/book/<int:book_id>/review", methods=["POST"])
@login_required
def submit_review(book_id):
    book = Book.query.get_or_404(book_id)
    user = get_current_user()

    # Prevent user from reviewing the same book twice
    existing_review = Review.query.filter_by(user_id=user.id, book_id=book_id).first()
    if existing_review:
        flash("You have already reviewed this book.", "warning")
        return redirect(url_for('main.book_detail', book_id=book_id))

    rating = request.form.get("rating")
    content = request.form.get("content")

    if not rating or not content:
        flash("Both rating and review content are required.", "danger")
        return redirect(url_for('main.book_detail', book_id=book_id))

    new_review = Review(
        user_id=user.id,
        book_id=book_id,
        rating=int(rating),
        content=content
    )
    db.session.add(new_review)
    db.session.commit()

    flash("Your review has been submitted successfully!", "success")
    return redirect(url_for('main.book_detail', book_id=book_id))

@main_bp.route("/download/book/<int:book_id>")
@login_required
def download_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.pdf_file:
        flash('No downloadable file found for this book.', 'warning')
        return redirect(url_for('main.book_detail', book_id=book.id))
    
    # Check if the user wants to view the file in the browser
    view_in_browser = request.args.get('view') == 'true'

    return send_from_directory(
        current_app.config['BOOK_PDF_FOLDER'], 
        book.pdf_file, 
        as_attachment=(not view_in_browser)
    )
@main_bp.route("/borrowing-history")
@login_required
def borrowing_history():
    user = get_current_user()
    query = Borrowing.query
    if user.role != 'admin':
        query = query.filter_by(user_id=user.id)
    borrowed_books = query.order_by(Borrowing.borrowed_date.desc()).all()
    return render_template("borrowing_history.html", current_user=user, borrowed_books=borrowed_books, now=datetime.utcnow())

@main_bp.route("/borrow/<int:book_id>")
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    user = get_current_user()
    if book.available_copies <= 0:
        flash("This book is currently unavailable.", "warning")
        return redirect(url_for('main.index'))
    new_borrowing = Borrowing(user_id=user.id, book_id=book.id, due_date=datetime.utcnow() + timedelta(days=14))
    book.available_copies -= 1
    db.session.add(new_borrowing)
    db.session.commit()
    flash(f"You have successfully borrowed '{book.title}'.", "success")
    return redirect(url_for('main.borrowing_history'))

@main_bp.route("/return/<int:borrow_id>")
@login_required
def return_book(borrow_id):
    borrowing_record = Borrowing.query.get_or_404(borrow_id)
    if borrowing_record.user_id != get_current_user().id and get_current_user().role != 'admin':
        flash("Not authorized to perform this action.", "danger")
        return redirect(url_for('main.borrowing_history'))
    if not borrowing_record.is_returned:
        borrowing_record.is_returned = True
        borrowing_record.returned_date = datetime.utcnow()
        borrowing_record.book.available_copies += 1
        db.session.commit()
        flash(f"You have successfully returned '{borrowing_record.book.title}'.", "success")
    else:
        flash("This book has already been returned.", "info")
    return redirect(url_for('main.borrowing_history'))


#==============================================================================
# ERROR HANDLERS
#==============================================================================

@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html", current_user=get_current_user()), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html", current_user=get_current_user()), 500

