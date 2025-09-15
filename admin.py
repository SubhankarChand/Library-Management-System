from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from extensions import db, admin
from models import User, Book, Borrowing, Review
from blueprints.auth import get_current_user

# This is a custom ModelView that will be used for all our admin pages
class SecureModelView(ModelView):
    """This class ensures that only users with the 'admin' role can see and use the admin pages."""
    def is_accessible(self):
        user = get_current_user()
        return user is not None and user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # Redirect non-admins to the main index page
        return redirect(url_for('main.index'))

# This is a custom IndexView for the main admin dashboard page
class SecureAdminIndexView(AdminIndexView):
    """This class secures the main admin index page."""
    def is_accessible(self):
        user = get_current_user()
        return user is not None and user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))

# ==============================================================================
# ======================== START: CORRECTED CONFIGURATION ======================
# ==============================================================================
# We add the name and url to ensure the link in the navbar works correctly and
# the main admin page has a proper title.
admin.index_view = SecureAdminIndexView(name="Control Panel Home", url="/admin")
# ========================= END: CORRECTED CONFIGURATION =======================

# Add the secure model views to the admin panel
# Now, you can manage Users, Books, etc., from the /admin URL
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Book, db.session))
admin.add_view(SecureModelView(Borrowing, db.session))
admin.add_view(SecureModelView(Review, db.session))

