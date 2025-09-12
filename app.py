import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from extensions import db, migrate, mail
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

    # Other database settings
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

    # File upload configuration
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["BOOK_COVER_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "covers")
    app.config["BOOK_PDF_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "pdfs")
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB
    
    # Allowed file extensions
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['ALLOWED_PDF_EXTENSIONS'] = {'pdf'}

    # Create upload directories
    for p in [app.config["UPLOAD_FOLDER"], app.config["BOOK_COVER_FOLDER"], app.config["BOOK_PDF_FOLDER"]]:
        os.makedirs(p, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # ==============================================================================
    # ============================ START: FIX FOR IMPORT ERROR =====================
    # ==============================================================================
    # By importing the function and setting up the scheduler inside the app factory,
    # we avoid the circular import error.
    from blueprints.main import send_due_date_reminders

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        lambda: send_due_date_reminders(app), 
        'cron', 
        hour=8, 
        minute=0
    )
    scheduler.start()
    # ============================= END: FIX FOR IMPORT ERROR ======================

    return app

# Run the app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

