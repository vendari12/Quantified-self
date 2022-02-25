from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()
login_manager = LoginManager()


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    


    #app.add_template_global(index_for_role)
    #app.jinja_env.globals.update(json_load=json_load, image_size=image_size)
    pass



