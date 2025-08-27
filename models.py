from datetime import datetime
from sqlalchemy import UniqueConstraint, Index, CheckConstraint, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, TINYINT
from sqlalchemy.orm import validates, relationship
from extensions import db

# ---------------- USERS ----------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(VARCHAR(100), unique=True, nullable=False)
    email = db.Column(VARCHAR(255), unique=True, nullable=False)
    password_hash = db.Column(VARCHAR(255), nullable=False)
    role = db.Column(VARCHAR(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    published_books = db.relationship("Book", backref="publisher", lazy=True, foreign_keys="Book.publisher_id")
    borrowings = db.relationship("Borrowing", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)

    @validates("role")
    def validate_role(self, key, value):
        if value not in ("admin", "publisher", "user"):
            raise ValueError("role must be one of: admin, publisher, user")
        return value

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

# ---------------- CATEGORIES ----------------
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(VARCHAR(100), unique=True, nullable=False)

    # Remove the relationship to books since we're using a simple string category
    # books = db.relationship("Book", backref="book_category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

# ---------------- BOOKS ----------------
class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(VARCHAR(200), nullable=False)
    author = db.Column(VARCHAR(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(VARCHAR(100))  # Simple string field, not foreign key
    cover_image = db.Column(VARCHAR(255))
    pdf_file = db.Column(VARCHAR(255))
    publisher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    borrowings = db.relationship("Borrowing", backref="book", lazy=True)
    reviews = db.relationship("Review", backref="book", lazy=True)

    __table_args__ = (
        Index("ix_books_title", "title"),
        Index("ix_books_author", "author"),
        CheckConstraint("available_copies >= 0", name="ck_books_available_nonneg"),
    )

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

# ---------------- BORROWINGS ----------------
class Borrowing(db.Model):
    __tablename__ = "borrowings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    status = db.Column(VARCHAR(20), default="borrowed")

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", "status", name="uq_active_borrow_per_user_book"),
    )

    @property
    def is_returned(self):
        return self.status == "returned"

    @property
    def borrowed_date(self):
        return self.borrow_date

    def __repr__(self):
        return f"<Borrowing u={self.user_id} b={self.book_id} status={self.status}>"

# ---------------- REVIEWS ----------------
class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    rating = db.Column(TINYINT(unsigned=True), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_1_5"),
        Index("ix_reviews_book_id", "book_id"),
        Index("ix_reviews_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<Review book={self.book_id} user={self.user_id} ★{self.rating}>"