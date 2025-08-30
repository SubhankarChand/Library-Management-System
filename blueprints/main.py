import re
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import current_app
from datetime import datetime, timedelta
from flask import (Blueprint, render_template, request, redirect,url_for, flash, session, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from .auth import login_required, admin_required, publisher_required, get_current_user
from models import User, Book, Category, Borrowing, Review


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


main_bp = Blueprint("main", __name__)
# ----- Borrowing History -----
@main_bp.route("/borrowing-history")
@login_required
def borrowing_history():
    user = get_current_user()
    borrowed_books = []

    # Admin sees all history, a regular user only sees their own
    if user.role == "admin":
        borrowed_books = Borrowing.query.order_by(Borrowing.borrowed_date.desc()).all()
    else:
        borrowed_books = Borrowing.query.filter_by(user_id=user.id).order_by(Borrowing.borrowed_date.desc()).all()

    return render_template("borrowing_history.html", current_user=user, borrowed_books=borrowed_books,now=datetime.utcnow())

# ----- Add/Edit/Delete Books -----
@main_bp.route("/add-book", methods=['GET', 'POST'])
@publisher_required
def add_book():
    if request.method == 'POST':
        # Form data
        title = request.form.get('title')
        author = request.form.get('author')
        # ... get other form data ...
        
        cover_image = request.files.get('cover_image')
        pdf_file = request.files.get('pdf_file')

        # --- File Handling ---
        cover_filename = None
        if cover_image and allowed_file(cover_image.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
            cover_filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(current_app.config['BOOK_COVER_FOLDER'], cover_filename))

        pdf_filename = None
        if pdf_file and allowed_file(pdf_file.filename, current_app.config['ALLOWED_PDF_EXTENSIONS']):
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(current_app.config['BOOK_PDF_FOLDER'], pdf_filename))
        
        # Create new book object and save to DB
        new_book = Book(
            title=title,
            author=author,
            # ... set other attributes ...
            publisher_id=get_current_user().id,
            cover_image=cover_filename,
            pdf_file=pdf_filename
        )
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('main.publisher_dashboard'))
        
    return render_template('book_form.html', current_user=get_current_user())

@main_bp.route("/download/book/<int:book_id>")
@login_required
def download_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.pdf_file:
        flash('No downloadable file found for this book.', 'warning')
        return redirect(url_for('main.index'))
    
    return send_from_directory(
        current_app.config['BOOK_PDF_FOLDER'], 
        book.pdf_file, 
        as_attachment=True
    )
    
#------ Retuen Books------#
@main_bp.route("/return/<int:borrow_id>")
@login_required
def return_book(borrow_id):
    # Find the specific borrowing record
    borrowing_record = Borrowing.query.get_or_404(borrow_id)
    user = get_current_user()

    # Security check: Make sure the user is returning their own book (or is an admin)
    if borrowing_record.user_id != user.id and user.role != 'admin':
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('main.borrowing_history'))

    # Check if the book is already returned
    if borrowing_record.is_returned:
        flash("This book has already been returned.", "info")
        return redirect(url_for('main.borrowing_history'))

    # Update the borrowing record
    borrowing_record.is_returned = True
    borrowing_record.returned_date = datetime.utcnow()

    # Increment the book's available copies
    borrowing_record.book.available_copies += 1

    db.session.commit()

    flash(f"You have successfully returned '{borrowing_record.book.title}'.", "success")
    return redirect(url_for('main.borrowing_history'))

# ----- Home -----
@main_bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    selected_category = request.args.get('category', '')
    selected_genre = request.args.get('genre', '')
    selected_book_type = request.args.get('book_type', '')
    selected_status = request.args.get('status', '')

    # Base query
    query = Book.query

    # Apply filters
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

    # Paginate the results
    books_pagination = query.order_by(Book.created_at.desc()).paginate(page=page, per_page=9)

    # Get distinct values for filters
    categories = [cat[0] for cat in db.session.query(Book.category).distinct().all() if cat[0]]
    genres = [g[0] for g in db.session.query(Book.genre).distinct().all() if g[0]]
    book_types = [bt[0] for bt in db.session.query(Book.book_type).distinct().all() if bt[0]]

    return render_template(
        "index.html",
        current_user=get_current_user(),
        books=books_pagination,
        search=search_query,
        categories=categories,
        genres=genres,
        book_types=book_types,
        selected_category=selected_category,
        selected_genre=selected_genre,
        selected_book_type=selected_book_type,
        selected_status=selected_status,
    )
    
@main_bp.route("/borrow/<int:book_id>")
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    user = get_current_user()

    # Deny access if not a regular user
    if user.role != 'user':
        flash("Only users can borrow books.", "danger")
        return redirect(url_for('main.index'))

    # Check if the book is available
    if book.available_copies <= 0:
        flash("Sorry, this book is currently not available.", "warning")
        return redirect(url_for('main.index'))

    # Check if the user has already borrowed this book and not returned it
    existing_borrow = Borrowing.query.filter_by(
        user_id=user.id,
        book_id=book.id,
        is_returned=False
    ).first()

    if existing_borrow:
        flash("You have already borrowed this book.", "info")
        return redirect(url_for('main.user_dashboard'))

    # Create a new borrowing record
    due_date = datetime.utcnow() + timedelta(days=14)  # Book is due in 2 weeks
    new_borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        due_date=due_date
    )

    # Decrement the available copies count
    book.available_copies -= 1

    db.session.add(new_borrowing)
    db.session.commit()

    flash(f"You have successfully borrowed '{book.title}'. It is due on {due_date.strftime('%Y-%m-%d')}.", "success")
    return redirect(url_for('main.user_dashboard'))

# ----- User Registration -----
@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        errors = []

        # Username validation
        if not username or len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters long.")
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append("Username can only contain letters, numbers, and underscores.")

        # Email validation
        if not email or not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors.append("Please enter a valid email address.")
        
        # Password validation
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one number.")
        elif not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter.")
        elif not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if role not in ["admin", "publisher", "user"]:
            errors.append("Please select a valid role.")

        # Duplicate checks
        if not errors:
            if User.query.filter_by(email=email).first():
                errors.append("Email already registered.")
            if User.query.filter_by(username=username).first():
                errors.append("Username already taken.")

        if errors:
            return render_template("register.html", errors=errors, form_data=request.form)

        # Save new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

# ----- Login -----
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact admin.", "danger")
                return redirect(url_for("main.login"))

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            flash(f"Welcome back, {user.username}!", "success")

            if user.role == "admin":
                return redirect(url_for("main.admin_dashboard"))
            elif user.role == "publisher":
                return redirect(url_for("main.publisher_dashboard"))
            else:
                return redirect(url_for("main.user_dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@main_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))

# ----- User Dashboard -----
@main_bp.route("/user/dashboard")
@login_required
def user_dashboard():
    user = get_current_user()
    if user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    stats = {
        "borrowed_count": Borrowing.query.filter_by(user_id=user.id, is_returned=False).count(),
        "overdue_count": Borrowing.query.filter(
            Borrowing.user_id == user.id,
            Borrowing.is_returned == False,
            Borrowing.due_date < datetime.utcnow(),
        ).count(),
        "total_books": Book.query.filter(Book.available_copies > 0).count(),
        "read_books": Borrowing.query.filter_by(user_id=user.id, is_returned=True).count(),
    }

    recent_borrowings = Borrowing.query.filter_by(user_id=user.id).order_by(
        Borrowing.borrowed_date.desc()
    ).limit(5).all()

    recommended_books = Book.query.filter(Book.available_copies > 0).order_by(db.func.random()).limit(3).all()

    return render_template(
        "user_dashboard.html",
        current_user=user,
        **stats,
        recent_borrowings=recent_borrowings,
        recommended_books=recommended_books,
    )

# ----- Admin Dashboard -----
@main_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    total_books = Book.query.count()
    total_users = User.query.count()
    total_publishers = User.query.filter_by(role="publisher").count()
    borrowed_books = Borrowing.query.filter_by(is_returned=False).count()

    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        "admin_dashboard.html",
        current_user=get_current_user(),
        total_books=total_books,
        total_users=total_users,
        total_publishers=total_publishers,
        total_borrowed=borrowed_books,
        recent_books=recent_books,
        recent_users=recent_users,
    )

# ----- Publisher Dashboard -----
@main_bp.route("/publisher/dashboard")
@publisher_required
def publisher_dashboard():
    user = get_current_user()
    published_books = Book.query.filter_by(publisher_id=user.id).all()

    borrowed_count = Borrowing.query.join(Book).filter(Book.publisher_id == user.id).count()
    available_copies = db.session.query(db.func.sum(Book.available_copies)).filter(
        Book.publisher_id == user.id
    ).scalar() or 0
    avg_rating = db.session.query(db.func.avg(Review.rating)).join(Book).filter(
        Book.publisher_id == user.id
    ).scalar() or 0

    return render_template(
        "publisher_dashboard.html",
        current_user=user,
        published_books=len(published_books),
        borrowed_count=borrowed_count,
        available_copies=available_copies,
        average_rating=float(avg_rating),
        books=published_books,
    )

# ----- API -----
@main_bp.route("/api/books")
def api_books():
    books = Book.query.all()
    return jsonify(
        [{"id": b.id, "title": b.title, "author": b.author, "isbn": b.isbn, "available_copies": b.available_copies} for b in books]
    )

@main_bp.route("/api/user/stats")
@login_required
def api_user_stats():
    user = get_current_user()
    stats = {
        "borrowed_count": Borrowing.query.filter_by(user_id=user.id, is_returned=False).count(),
        "read_books": Borrowing.query.filter_by(user_id=user.id, is_returned=True).count(),
    }
    return jsonify(stats)

# ----- Errors -----
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html", current_user=get_current_user()), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html", current_user=get_current_user()), 500
