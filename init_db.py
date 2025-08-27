from app import create_app, db
from models import User, Book, Category, Borrowing, Review
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create default admin user
        admin_user = User.query.filter_by(email='admin@library.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@library.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            print("Created admin user")
        
        # Create a sample publisher
        publisher_user = User.query.filter_by(email='publisher@example.com').first()
        if not publisher_user:
            publisher_user = User(
                username='bookpublisher',
                email='publisher@example.com',
                password_hash=generate_password_hash('publisher123'),
                role='publisher'
            )
            db.session.add(publisher_user)
            print("Created publisher user")
        
        # Create a sample regular user
        regular_user = User.query.filter_by(email='user@example.com').first()
        if not regular_user:
            regular_user = User(
                username='reader123',
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                role='user'
            )
            db.session.add(regular_user)
            print("Created regular user")
        
        # Create categories
        categories = [
            'Energy, Climate and Sustainability',
            'Health Sciences', 
            'Engineering and Technology',
            'Law',
            'Design',
            'Architecture and Planning',
            'Humanities & Arts',
            'Management & Commerce',
            'Maths & Sciences',
            'Education',
            'General'
        ]
        
        for cat_name in categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.session.add(category)
        
        db.session.commit()
        print("Created categories")
        
        # Create sample books (only if publisher exists)
        if publisher_user:
            sample_books = [
                {
                    'title': 'Introduction to Python Programming',
                    'author': 'John Smith',
                    'description': 'A comprehensive guide to Python programming for beginners.',
                    'category': 'Engineering and Technology',
                    'available_copies': 5
                },
                {
                    'title': 'Climate Change Solutions',
                    'author': 'Dr. Emily Johnson',
                    'description': 'Exploring innovative solutions to address climate change challenges.',
                    'category': 'Energy, Climate and Sustainability', 
                    'available_copies': 3
                },
                {
                    'title': 'Advanced Data Structures',
                    'author': 'Robert Williams',
                    'description': 'In-depth analysis of data structures and algorithms.',
                    'category': 'Maths & Sciences',
                    'available_copies': 2
                }
            ]
            
            for book_data in sample_books:
                book = Book(
                    title=book_data['title'],
                    author=book_data['author'],
                    description=book_data['description'],
                    category=book_data['category'],
                    publisher_id=publisher_user.id,
                    available_copies=book_data['available_copies']
                )
                db.session.add(book)
            
            print("Created sample books")
        
        db.session.commit()
        print("Database initialized successfully!")
        print("\n=== Login Credentials ===")
        print("Admin: admin@library.com / admin123")
        print("Publisher: publisher@example.com / publisher123") 
        print("User: user@example.com / user123")

if __name__ == '__main__':
    init_database()