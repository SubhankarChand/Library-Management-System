from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_admin import Admin

# Initialize the extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

admin = Admin(name='KitabGhar Control Panel')