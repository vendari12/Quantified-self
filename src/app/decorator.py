from functools import wraps
from flask import abort, flash
from flask_login import current_user
from app.models import Permission




def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash("You don't have permission to perform this action")
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator



def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
