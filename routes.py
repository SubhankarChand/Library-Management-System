from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from models import User, Book, BorrowedBook
from auth import login_required, admin_required, publisher_required, get_current_user
from werkzeug.security import generate_password_hash

@app.route('/')
def index():
    books = Book.query.filter(Book.available_copies > 0).all()
    current_user = get_current_user()
    return render_template('index.html', books=books, current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to appropriate dashboard
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'publisher':
                return redirect(url_for('publisher_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    current_user = get_current_user()
    if current_user.role != 'user':
        return redirect(url_for('index'))
    
    # Get user's current borrowed books
    borrowed_books = BorrowedBook.query.filter_by(
        user_id=current_user.id, 
        is_returned=False
    ).all()
    
    # Get available books
    available_books = Book.query.filter(Book.available_copies > 0).all()
    
    return render_template('user_dashboard.html', 
                         borrowed_books=borrowed_books, 
                         available_books=available_books,
                         current_user=current_user)

@app.route('/publisher_dashboard')
@publisher_required
def publisher_dashboard():
    current_user = get_current_user()
    published_books = Book.query.filter_by(publisher_id=current_user.id).all()
    return render_template('publisher_dashboard.html', 
                         published_books=published_books,
                         current_user=current_user)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    current_user = get_current_user()
    total_users = User.query.count()
    total_books = Book.query.count()
    total_borrowed = BorrowedBook.query.filter_by(is_returned=False).count()
    
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_borrowed=total_borrowed,
                         recent_books=recent_books,
                         recent_users=recent_users,
                         current_user=current_user)

@app.route('/add_book', methods=['GET', 'POST'])
@publisher_required
def add_book():
    current_user = get_current_user()
    
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            genre=request.form['genre'],
            description=request.form['description'],
            publication_year=int(request.form['publication_year']),
            total_copies=int(request.form['total_copies']),
            available_copies=int(request.form['total_copies']),
            publisher_id=current_user.id
        )
        
        try:
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('publisher_dashboard'))
        except Exception as e:
            flash('Error adding book. ISBN might already exist.', 'danger')
            db.session.rollback()
    
    return render_template('book_form.html', current_user=current_user)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@publisher_required
def edit_book(book_id):
    current_user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    # Check if the current user is the publisher of this book
    if book.publisher_id != current_user.id and current_user.role != 'admin':
        flash('You can only edit books you published.', 'danger')
        return redirect(url_for('publisher_dashboard'))
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.genre = request.form['genre']
        book.description = request.form['description']
        book.publication_year = int(request.form['publication_year'])
        
        # Update copies carefully
        new_total = int(request.form['total_copies'])
        borrowed_count = book.total_copies - book.available_copies
        book.total_copies = new_total
        book.available_copies = max(0, new_total - borrowed_count)
        
        try:
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('publisher_dashboard'))
        except Exception as e:
            flash('Error updating book.', 'danger')
            db.session.rollback()
    
    return render_template('edit_book.html', book=book, current_user=current_user)

@app.route('/delete_book/<int:book_id>')
@publisher_required
def delete_book(book_id):
    current_user = get_current_user()
    book = Book.query.get_or_404(book_id)
    
    # Check if the current user is the publisher of this book
    if book.publisher_id != current_user.id and current_user.role != 'admin':
        flash('You can only delete books you published.', 'danger')
        return redirect(url_for('publisher_dashboard'))
    
    # Check if book is currently borrowed
    active_borrows = BorrowedBook.query.filter_by(book_id=book_id, is_returned=False).count()
    if active_borrows > 0:
        flash('Cannot delete book that is currently borrowed.', 'danger')
        return redirect(url_for('publisher_dashboard'))
    
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('publisher_dashboard'))

@app.route('/borrow_book/<int:book_id>')
@login_required
def borrow_book(book_id):
    current_user = get_current_user()
    
    if current_user.role != 'user':
        flash('Only users can borrow books.', 'danger')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    
    if not book.is_available:
        flash('This book is not available for borrowing.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Check if user already has this book borrowed
    existing_borrow = BorrowedBook.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        is_returned=False
    ).first()
    
    if existing_borrow:
        flash('You have already borrowed this book.', 'warning')
        return redirect(url_for('user_dashboard'))
    
    # Create borrow record
    borrow = BorrowedBook(
        user_id=current_user.id,
        book_id=book_id,
        due_date=datetime.utcnow() + timedelta(days=14)  # 2 weeks loan period
    )
    
    # Update book availability
    book.available_copies -= 1
    
    db.session.add(borrow)
    db.session.commit()
    
    flash(f'You have successfully borrowed "{book.title}".', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/return_book/<int:borrow_id>')
@login_required
def return_book(borrow_id):
    current_user = get_current_user()
    borrow = BorrowedBook.query.get_or_404(borrow_id)
    
    if borrow.user_id != current_user.id and current_user.role != 'admin':
        flash('You can only return books you borrowed.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if borrow.is_returned:
        flash('This book has already been returned.', 'warning')
        return redirect(url_for('user_dashboard'))
    
    # Mark as returned
    borrow.is_returned = True
    borrow.returned_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(borrow.book_id)
    book.available_copies += 1
    
    db.session.commit()
    
    flash(f'You have successfully returned "{book.title}".', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/borrowing_history')
@login_required
def borrowing_history():
    current_user = get_current_user()
    
    if current_user.role == 'user':
        borrowed_books = BorrowedBook.query.filter_by(user_id=current_user.id).order_by(BorrowedBook.borrowed_date.desc()).all()
    else:
        borrowed_books = BorrowedBook.query.order_by(BorrowedBook.borrowed_date.desc()).all()
    
    return render_template('borrowing_history.html', 
                         borrowed_books=borrowed_books,
                         current_user=current_user)

@app.route('/manage_users')
@admin_required
def manage_users():
    current_user = get_current_user()
    users = User.query.all()
    return render_template('manage_users.html', users=users, current_user=current_user)

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deletion of admin users
    if user.role == 'admin':
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check for active borrows
    active_borrows = BorrowedBook.query.filter_by(user_id=user_id, is_returned=False).count()
    if active_borrows > 0:
        flash('Cannot delete user with active book borrows.', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('manage_users'))
