from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, publisher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    published_books = db.relationship('Book', backref='publisher_user', lazy=True, foreign_keys='Book.publisher_id')
    borrowed_books = db.relationship('BorrowedBook', backref='borrower', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False, default='General')
    book_type = db.Column(db.String(50), nullable=False, default='Physical')
    description = db.Column(db.Text)
    publication_year = db.Column(db.Integer)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    publisher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    borrowed_records = db.relationship('BorrowedBook', backref='book', lazy=True)
    
    @property
    def is_available(self):
        return self.available_copies > 0
    
    def __repr__(self):
        return f'<Book {self.title}>'

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrowed_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_date = db.Column(db.DateTime)
    is_returned = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<BorrowedBook User:{self.user_id} Book:{self.book_id}>'
