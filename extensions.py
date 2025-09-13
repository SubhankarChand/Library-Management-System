from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_admin import Admin

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
# This creates the main admin interface, using a professional Bootstrap 4 theme
admin = Admin(name='KitabGhar Control Panel', template_mode='bootstrap4')

