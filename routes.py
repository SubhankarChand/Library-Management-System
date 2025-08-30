import re
from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from extensions import db
from auth import login_required, admin_required, publisher_required, get_current_user
from flask import Blueprint, render_template
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Book, Category, Borrowing, Review

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
     return render_template("index.html")
 
# List all books
@main_bp.route("/books")
def list_books():
    books = Book.query.all()
    return render_template("books.html", books=books)
# Add new book
@main_bp.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        category_id = request.form.get("category_id")

        if not title or not author:
            flash("Title and author are required!", "danger")
            return redirect(url_for("main.add_book"))

        new_book = Book(title=title, author=author, category_id=category_id)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for("main.list_books"))

    categories = Category.query.all()
    return render_template("add_book.html", categories=categories)

# User registration (simple example)
@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            flash("Name and email are required!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("main.home"))

    return render_template("register.html")

# ----- Helper Functions -----
def get_user_stats(user_id):
    """Get statistics for user dashboard"""
    borrowed_count = Borrowing.query.filter_by(user_id=user_id, is_returned=False).count()
    overdue_count = Borrowing.query.filter(
        Borrowing.user_id == user_id,
        Borrowing.is_returned == False,
        Borrowing.due_date < datetime.utcnow()
    ).count()
    total_books = Book.query.filter(Book.available_copies > 0).count()
    
    return {
        'borrowed_count': borrowed_count,
        'overdue_count': overdue_count,
        'total_books': total_books,
        'read_books': Borrowing.query.filter_by(user_id=user_id, is_returned=True).count()
    }

def get_publisher_stats(publisher_id):
    """Get statistics for publisher dashboard"""
    published_books = Book.query.filter_by(publisher_id=publisher_id).count()
    borrowed_count = Borrowing.query.join(Book).filter(Book.publisher_id == publisher_id).count()
    available_copies = db.session.query(db.func.sum(Book.available_copies)).filter(
        Book.publisher_id == publisher_id
    ).scalar() or 0
    
    # Calculate average rating
    avg_rating = db.session.query(db.func.avg(Review.rating)).join(Book).filter(
        Book.publisher_id == publisher_id
    ).scalar() or 0
    
    return {
        'published_books': published_books,
        'borrowed_count': borrowed_count,
        'available_copies': available_copies,
        'average_rating': float(avg_rating)
    }

# ----- Authentication Routes -----
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        publisher_name = request.form.get('publisher_name', '')
        publisher_type = request.form.get('publisher_type', '')
        
        # Input validation
        errors = []
        
        # Validate username
        if not username or len(username.strip()) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        # Validate email
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please enter a valid email address.')
        
        # Validate password
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif not any(char.isdigit() for char in password):
            errors.append('Password must contain at least one number.')
        elif not any(char.isupper() for char in password):
            errors.append('Password must contain at least one uppercase letter.')
        elif not any(char.islower() for char in password):
            errors.append('Password must contain at least one lowercase letter.')
        
        # Validate password confirmation
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Validate role
        valid_roles = ['admin', 'publisher', 'user']
        if role not in valid_roles:
            errors.append('Please select a valid role.')
        
        # Check if user exists (only if no validation errors so far)
        if not errors:
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')
            
            if User.query.filter_by(username=username).first():
                errors.append('Username already taken.')
        
        # If there are errors, show them and return to form with data
        if errors:
            form_data = {
                'username': username,
                'email': email,
                'role': role,
                'publisher_name': publisher_name,
                'publisher_type': publisher_type
            }
            return render_template('register.html', 
                                 errors=errors,
                                 form_data=form_data)
        
        # Create new user if no errors
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'publisher':
                return redirect(url_for('publisher_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))  # Changed from 'home' to 'index'

# ----- Main Routes -----
def index():
    # Fetch some books to display on the home page
    books = Book.query.filter(Book.available_copies > 0).order_by(Book.created_at.desc()).limit(6).all()
    
    # Get unique categories and book types for filters
    categories = [cat[0] for cat in db.session.query(Book.category).distinct().all() if cat[0]]
    book_types = [bt[0] for bt in db.session.query(Book.book_type).distinct().all() if bt[0]]
    
    return render_template('index.html', 
                         current_user=get_current_user(),
                         books=books,
                         search='',
                         selected_category='',
                         selected_book_type='',
                         selected_status='',
                         categories=categories,
                         book_types=book_types)

def user_dashboard():
    user = get_current_user()
    if user.role != 'user':
        flash('Access denied. User dashboard is for regular users only.', 'danger')
        return redirect(url_for('index'))  # Changed from 'home' to 'index'
    
    stats = get_user_stats(user.id)
    recent_borrowings = Borrowing.query.filter_by(user_id=user.id).order_by(
        Borrowing.borrowed_date.desc()
    ).limit(5).all()
    
    # Get recommended books (simple implementation)
    recommended_books = Book.query.filter(
        Book.available_copies > 0
    ).order_by(db.func.random()).limit(3).all()
    
    return render_template('user_dashboard.html',
                         current_user=user,
                         borrowed_count=stats['borrowed_count'],
                         overdue_count=stats['overdue_count'],
                         total_books=stats['total_books'],
                         read_books=stats['read_books'],
                         recent_borrowings=recent_borrowings,
                         recommended_books=recommended_books)

def admin_dashboard():
    # Get stats for admin dashboard
    total_books = Book.query.count()
    total_users = User.query.count()
    total_publishers = User.query.filter_by(role='publisher').count()
    borrowed_books = Borrowing.query.filter_by(is_returned=False).count()
    
    # Get recent books and users
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         current_user=get_current_user(),
                         total_books=total_books,
                         total_users=total_users,
                         total_publishers=total_publishers,
                         total_borrowed=borrowed_books,
                         recent_books=recent_books,
                         recent_users=recent_users)

def publisher_dashboard():
    user = get_current_user()
    stats = get_publisher_stats(user.id)
    books = Book.query.filter_by(publisher_id=user.id).all()
    
    return render_template('publisher_dashboard.html',
                         current_user=user,
                         published_books=stats['published_books'],
                         borrowed_count=stats['borrowed_count'],
                         available_copies=stats['available_copies'],
                         average_rating=stats['average_rating'],
                         books=books)

# ----- Book Management Routes -----
def books_index():
    # Implement book search and filtering
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    book_type = request.args.get('book_type', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) |
            (Book.author.ilike(f'%{search}%')) |
            (Book.isbn.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter(Book.category == category)
    
    if book_type:
        query = query.filter(Book.book_type == book_type)
    
    if status == 'available':
        query = query.filter(Book.available_copies > 0)
    elif status == 'checked_out':
        query = query.filter(Book.available_copies == 0)
    
    books = query.order_by(Book.title).paginate(page=page, per_page=12)
    
    # Get unique categories and book types for filters
    categories = [cat[0] for cat in db.session.query(Book.category).distinct().all() if cat[0]]
    book_types = [bt[0] for bt in db.session.query(Book.book_type).distinct().all() if bt[0]]
    
    return render_template('index.html',
                         current_user=get_current_user(),
                         books=books,
                         search=search,
                         selected_category=category,
                         selected_book_type=book_type,
                         selected_status=status,
                         categories=categories,
                         book_types=book_types)

def add_book():
    if request.method == 'POST':
        # Extract form data
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        genre = request.form['genre']
        category = request.form['category']
        book_type = request.form['book_type']
        publication_year = request.form['publication_year']
        total_copies = request.form['total_copies']
        description = request.form.get('description', '')
        
        # Create new book
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            genre=genre,
            category=category,
            book_type=book_type,
            publication_year=publication_year,
            total_copies=total_copies,
            available_copies=total_copies,
            description=description,
            publisher_id=session['user_id']
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('publisher_dashboard'))
    
    return render_template('book_form.html', current_user=get_current_user())

def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Check if current user owns this book
    if book.publisher_id != session['user_id']:
        flash('You can only edit your own books.', 'danger')
        return redirect(url_for('publisher_dashboard'))
    
    if request.method == 'POST':
        # Update book details
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.genre = request.form['genre']
        book.category = request.form['category']
        book.book_type = request.form['book_type']
        book.publication_year = request.form['publication_year']
        
        # Handle copies update carefully
        new_total = int(request.form['total_copies'])
        if new_total >= (book.total_copies - book.available_copies):
            book.total_copies = new_total
            book.available_copies = new_total - (book.total_copies - book.available_copies)
        else:
            flash('Cannot reduce total copies below currently borrowed copies.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))
        
        book.description = request.form.get('description', '')
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('publisher_dashboard'))
    
    return render_template('edit_book.html', current_user=get_current_user(), book=book)

# ----- Borrowing Routes -----
def borrow_book(book_id):
    user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    if user.role != 'user':
        flash('Only regular users can borrow books.', 'danger')
        return redirect(url_for('books_index'))
    
    if not book.is_available:
        flash('This book is not available for borrowing.', 'danger')
        return redirect(url_for('index'))
    
    # Check if user already has this book borrowed
    existing_borrow = Borrowing.query.filter_by(
        user_id=user.id,
        book_id=book_id,
        is_returned=False
    ).first()
    
    if existing_borrow:
        flash('You have already borrowed this book.', 'warning')
        return redirect(url_for('index'))
    
    # Create borrowing record
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book_id,
        borrowed_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14)  # 2 weeks borrowing period
    )
    
    # Update book availability
    book.available_copies -= 1
    
    db.session.add(borrowing)
    db.session.commit()
    
    flash(f'Successfully borrowed "{book.title}"! Due date: {borrowing.due_date.strftime("%Y-%m-%d")}', 'success')
    return redirect(url_for('user_dashboard'))

def return_book(borrow_id):
    borrowing = Borrowing.query.get_or_404(borrow_id)
    user = get_current_user()
    
    # Check if current user owns this borrowing record
    if borrowing.user_id != user.id and user.role != 'admin':
        flash('You can only return your own borrowed books.', 'danger')
        return redirect(url_for('borrowing_history'))
    
    if borrowing.is_returned:
        flash('This book has already been returned.', 'warning')
        return redirect(url_for('borrowing_history'))
    
    # Update borrowing record
    borrowing.is_returned = True
    borrowing.returned_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(borrowing.book_id)
    book.available_copies += 1
    
    db.session.commit()
    
    flash(f'Successfully returned "{book.title}"!', 'success')
    return redirect(url_for('borrowing_history'))

def borrowing_history():
    user = get_current_user()
    
    if user.role == 'user':
        # Show only user's own history
        borrowed_books = Borrowing.query.filter_by(user_id=user.id).order_by(
            Borrowing.borrowed_date.desc()
        ).all()
    else:
        # Show all history for admins/publishers
        borrowed_books = Borrowing.query.order_by(
            Borrowing.borrowed_date.desc()
        ).all()
    
    return render_template('borrowing_history.html',
                         current_user=user,
                         borrowed_books=borrowed_books)

# ----- User Management Routes (Admin only) -----
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('manage_users.html', current_user=get_current_user(), users=users)

def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting admin accounts
    if user.role == 'admin':
        flash('Cannot delete administrator accounts.', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check if user has any books or borrowings
    has_books = Book.query.filter_by(publisher_id=user_id).count() > 0
    has_borrowings = Borrowing.query.filter_by(user_id=user_id).count() > 0
    
    if has_books or has_borrowings:
        # Deactivate instead of delete
        user.is_active = False
        flash(f'User {user.username} has been deactivated (cannot delete users with activity).', 'warning')
    else:
        db.session.delete(user)
        flash(f'User {user.username} has been deleted.', 'success')
    
    db.session.commit()
    return redirect(url_for('manage_users'))

def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating admin accounts
    if user.role == 'admin':
        flash('Cannot deactivate administrator accounts.', 'danger')
        return redirect(url_for('manage_users'))
    
    user.is_active = not user.is_active
    status = "activated" if user.is_active else "deactivated"
    
    db.session.commit()
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('manage_users'))

# ----- E-book Download Routes -----
def download_book(book_id):
    user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    if user.role != 'user':
        flash('Only regular users can download books.', 'danger')
        return redirect(url_for('books_index'))
    
    if book.book_type != 'E-book':
        flash('This book is not available for download.', 'danger')
        return redirect(url_for('index'))
    
    if not book.pdf_file_path:
        flash('Download not available for this book.', 'danger')
        return redirect(url_for('index'))
    
    # Record download activity (you might want to create a Download model)
    flash(f'Download started for "{book.title}"', 'success')
    
    # In a real application, you would serve the file here
    # For now, we'll just redirect back
    return redirect(url_for('user_dashboard'))

# ----- Review Routes -----
def add_review(book_id):
    user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    if user.role != 'user':
        flash('Only regular users can submit reviews.', 'danger')
        return redirect(url_for('books_index'))
    
    rating = request.form.get('rating')
    content = request.form.get('content')
    
    if not rating or not content:
        flash('Please provide both rating and review content.', 'danger')
        return redirect(url_for('index'))
    
    # Check if user has already reviewed this book
    existing_review = Review.query.filter_by(user_id=user.id, book_id=book_id).first()
    if existing_review:
        flash('You have already reviewed this book.', 'warning')
        return redirect(url_for('index'))
    
    # Create new review
    review = Review(
        user_id=user.id,
        book_id=book_id,
        rating=int(rating),
        content=content
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Thank you for your review!', 'success')
    return redirect(url_for('index'))

# ----- Error Handlers -----
def not_found_error(error):
    return render_template('404.html', current_user=get_current_user()), 404

def internal_error(error):
    db.session.rollback()
    return render_template('500.html', current_user=get_current_user()), 500

# ----- API Routes (optional) -----
def api_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'genre': book.genre,
        'available_copies': book.available_copies
    } for book in books])

def api_user_stats():
    user = get_current_user()
    stats = get_user_stats(user.id)
    return jsonify(stats)

def register_routes(app):
    """Register all routes with the app"""
    # Register all routes
    app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
    app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout)
    app.add_url_rule('/', view_func=index)  # Added this line
    app.add_url_rule('/user/dashboard', view_func=user_dashboard)
    app.add_url_rule('/admin/dashboard', view_func=admin_dashboard)
    app.add_url_rule('/publisher/dashboard', view_func=publisher_dashboard)
    app.add_url_rule('/books', view_func=books_index)
    app.add_url_rule('/book/add', view_func=add_book, methods=['GET', 'POST'])
    app.add_url_rule('/book/edit/<int:book_id>', view_func=edit_book, methods=['GET', 'POST'])
    app.add_url_rule('/borrow/<int:book_id>', view_func=borrow_book)
    app.add_url_rule('/return/<int:borrow_id>', view_func=return_book)
    app.add_url_rule('/borrowing-history', view_func=borrowing_history)
    app.add_url_rule('/admin/users', view_func=manage_users)
    app.add_url_rule('/admin/user/delete/<int:user_id>', view_func=delete_user)
    app.add_url_rule('/admin/user/toggle/<int:user_id>', view_func=toggle_user_status)
    app.add_url_rule('/download/<int:book_id>', view_func=download_book)
    app.add_url_rule('/review/<int:book_id>', view_func=add_review, methods=['POST'])
    app.add_url_rule('/api/books', view_func=api_books)
    app.add_url_rule('/api/user/stats', view_func=api_user_stats)
    
    # Error handlers
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)