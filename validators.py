import re
from flask import flash
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        flash('Please enter a valid email address.', 'danger')
        return False
    return True

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return False
    if not any(char.isdigit() for char in password):
        flash('Password must contain at least one number.', 'danger')
        return False
    if not any(char.isupper() for char in password):
        flash('Password must contain at least one uppercase letter.', 'danger')
        return False
    return True

def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        flash('Username must be at least 3 characters long.', 'danger')
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        flash('Username can only contain letters, numbers, and underscores.', 'danger')
        return False
    return True

def validate_book_data(form_data):
    """Validate book form data"""
    errors = []
    
    if not form_data.get('title') or len(form_data['title'].strip()) < 1:
        errors.append('Book title is required.')
    
    if not form_data.get('author') or len(form_data['author'].strip()) < 1:
        errors.append('Author name is required.')
    
    if form_data.get('publication_year'):
        try:
            year = int(form_data['publication_year'])
            current_year = datetime.now().year
            if year < 1000 or year > current_year:
                errors.append(f'Publication year must be between 1000 and {current_year}.')
        except ValueError:
            errors.append('Publication year must be a valid number.')
    
    if form_data.get('total_copies'):
        try:
            copies = int(form_data['total_copies'])
            if copies < 1:
                errors.append('Total copies must be at least 1.')
        except ValueError:
            errors.append('Total copies must be a valid number.')
    
    return errors