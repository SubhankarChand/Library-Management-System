import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, migrate

# ---- App Factory ----
def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

    # ---- DB URI (MySQL via PyMySQL) ----
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:subha12345@localhost:3306/KitabGhar?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

    # ---- File uploads ----
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
    app.config["BOOK_COVER_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "covers")
    app.config["BOOK_PDF_FOLDER"]   = os.path.join(app.config["UPLOAD_FOLDER"], "pdfs")
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

    # make folders if missing
    for p in [app.config["UPLOAD_FOLDER"], app.config["BOOK_COVER_FOLDER"], app.config["BOOK_PDF_FOLDER"]]:
        os.makedirs(p, exist_ok=True)

    # ---- Init extensions ----
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic sees them
    with app.app_context():
        from models import User, Book, Category, Borrowing, Review  # noqa: F401

    # ---- Register routes ----
    from routes import register_routes
    register_routes(app)

    return app

# Create app instance for direct execution
app = create_app()

# Dev entrypoint
if __name__ == "__main__":
    app.run(debug=True)