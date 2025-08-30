import os
import re
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from extensions import db, migrate


# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Security middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configuration from environment variables with fallbacks
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", 
        "mysql+pymysql://root:subha12345@localhost:3306/KitabGhar?charset=utf8mb4"
    )
    
    # CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get("CSRF_SECRET", "csrf-secret-key-change-in-production")
    
    # Other database settings
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

    # File upload configuration
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
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
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Register blueprints
    from auth import auth_bp
    from routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)