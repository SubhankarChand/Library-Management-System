from app import create_app, db
from models import User, Book

def test_database():
    app = create_app()
    
    with app.app_context():
        # Test if we can query users
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.role}")
        
        # Test if we can query books
        books = Book.query.all()
        print(f"\nFound {len(books)} books:")
        for book in books:
            print(f"  - {book.title} by {book.author}")
        
        print("\nDatabase connection successful! ✅")

if __name__ == '__main__':
    test_database()