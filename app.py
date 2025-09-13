import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from extensions import db, migrate, mail, admin
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Security middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configuration from environment variables
    app.secret_key = os.environ.get("SESSION_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    
    # CSRF protection
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get("CSRF_SECRET")
    
    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('KitabGhar', os.environ.get('MAIL_USERNAME'))
    
    # ==============================================================================
    # ========================== START: FLASK-ADMIN THEME ==========================
    # ==============================================================================
    # This line tells Flask-Admin to use a modern Bootstrap 4 theme
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    # =========================== END: FLASK-ADMIN THEME ===========================

    # Other database settings
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

    # File upload configuration
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["BOOK_COVER_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "covers")
    app.config["BOOK_PDF_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "pdfs")
    app.config["AVATAR_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "avatars")
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['ALLOWED_PDF_EXTENSIONS'] = {'pdf'}

    # Create all upload directories if they don't exist
    for p in [
        app.config["UPLOAD_FOLDER"], 
        app.config["BOOK_COVER_FOLDER"], 
        app.config["BOOK_PDF_FOLDER"],
        app.config["AVATAR_FOLDER"]
    ]:
        os.makedirs(p, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    admin.init_app(app) # Initialize Flask-Admin
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    from blueprints.main import send_due_date_reminders
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        lambda: send_due_date_reminders(app), 
        'cron', 
        hour=8, 
        minute=0
    )
    scheduler.start()

    return app

# Run the app
app = create_app()

# This is a new import for the admin setup
import admin as admin_setup

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

