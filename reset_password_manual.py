import os
import sys
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- IMPORTANT: Load the .env file ---
load_dotenv()

from app import create_app
from extensions import db
from models import User

def reset_user_password():
    """A command-line tool to manually reset a user's password."""
    app = create_app()
    with app.app_context():
        print("--- Manual Password Reset for KitabGhar ---")
        
        email = input("Enter the email of the account to reset: ").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"\nError: No user found with the email '{email}'.")
            return

        print(f"\nFound user: {user.username} (Role: {user.role})")
        print("NOTE: Your password will be visible as you type.")
        
        new_password = input("Enter the new password: ")
        confirm_password = input("Confirm the new password: ")

        if new_password != confirm_password:
            print("\nError: Passwords do not match. Aborting.")
            return
            
        if len(new_password) < 8:
            print("\nError: Password must be at least 8 characters long. Aborting.")
            return

        try:
            # Generate the new secure password hash
            user.password_hash = generate_password_hash(new_password)
            
            print("\nUpdating password in the database...")
            # Commit the change to the database
            db.session.commit()
            
            print("\nSuccess!")
            print(f"The password for '{user.username}' has been successfully updated.")

        except Exception as e:
            db.session.rollback()
            print(f"\nAn error occurred while updating the database: {e}")
            print("The password was NOT updated. Please try again.")

if __name__ == '__main__':
    reset_user_password()

