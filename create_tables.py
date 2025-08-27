from app import create_app, db
from models import User, Book, Category, Borrowing, Review

def create_tables():
    app = create_app()
    
    with app.app_context():
        # Create all tables based on your models
        db.create_all()
        print("All tables created successfully!")
        
        # Verify tables were created (updated method for newer SQLAlchemy)
        inspector = db.engine.inspector
        tables = inspector.get_table_names()
        print("Tables in database:", tables)

if __name__ == '__main__':
    create_tables()