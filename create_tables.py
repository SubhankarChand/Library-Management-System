from app import create_app, db
from models import User, Book, Category, Borrowing, Review
from sqlalchemy import inspect

def create_tables():
    app = create_app()
    
    with app.app_context():
        # Create all tables based on your models
        db.create_all()
        print("All tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Tables in database:", tables)

if __name__ == '__main__':
    create_tables()