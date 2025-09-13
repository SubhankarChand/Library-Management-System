from extensions import db
from datetime import datetime

# ==============================================================================
# DATABASE MODELS
# ==============================================================================

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ==============================================================================
    # ========================== START: NEW PROFILE FIELDS =========================
    # ==============================================================================
    profile_picture = db.Column(db.String(255), nullable=True, default='default.png')
    dob = db.Column(db.Date, nullable=True)
    school_college = db.Column(db.String(200), nullable=True)
    # =========================== END: NEW PROFILE FIELDS ==========================
    
    # Relationships
    books = db.relationship('Book', back_populates='publisher', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='user', lazy=True, cascade="all, delete-orphan")
    borrowings = db.relationship('Borrowing', back_populates='user', lazy=True, cascade="all, delete-orphan")

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    book_type = db.Column(db.String(50))
    publication_year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    total_copies = db.Column(db.Integer, default=1, nullable=False)
    available_copies = db.Column(db.Integer, default=1, nullable=False)
    cover_image = db.Column(db.String(255))
    pdf_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    publisher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    publisher = db.relationship('User', back_populates='books')
    reviews = db.relationship('Review', back_populates='book', lazy=True, cascade="all, delete-orphan")
    borrowings = db.relationship('Borrowing', back_populates='book', lazy=True, cascade="all, delete-orphan")

class Borrowing(db.Model):
    __tablename__ = 'borrowing'
    id = db.Column(db.Integer, primary_key=True)
    borrowed_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False, nullable=False)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='borrowings')
    book = db.relationship('Book', back_populates='borrowings')

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='reviews')
    book = db.relationship('Book', back_populates='reviews')
