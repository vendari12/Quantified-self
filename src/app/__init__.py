import json, os, operator, logging
from flask import Flask, request as req
from flask_sqlalchemy import SQLAlchemy
#from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from app.models import *
from app.utils import login_manager
from config import config

basedir = os.path.abspath(os.path.dirname(__file__))


async_mode = None



csrf = CSRFProtect()
#compress = Compress()
#images = UploadSet('images', IMAGES)
# Set up Flask-Login
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'
#s3 = FlaskS3()



#from elasticsearch import Elasticsearch
import app.models as models

#recaptcha = ReCaptcha()




def json_load(string):
    return json.loads(string)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if app.debug != True:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_SIZE'] = 500
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 100
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
        app.config['SQLALCHEMY_POOL_TIMEOUT'] = 50
    
    # not using sqlalchemy event system, hence disabling it
    app.config['UPLOADED_IMAGES_DEST'] = '/home/ubuntu/flaskapp/flask-base/appstatic/photo/' if \
        not os.environ.get('UPLOADED_IMAGES_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_IMAGES_DEST')
   
    app.config["DEBUG"] = True
    app.config["SESSION_TYPE"] = 'filesystem'

    config[config_name].init_app(app)
    

    db = SQLAlchemy(app, session_options={
        'expire_on_commit': False})
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    # Set up extensions
    login_manager.init_app(app)
    csrf.init_app(app)
    #configure_uploads(app, images)
    
    #cache.init_app(app)


    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)



    # Create app blueprints
    from .blueprints.public import public as public_blueprint
    app.register_blueprint(public_blueprint)

    from .blueprints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .blueprints.account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')



    #@app.cli.command()
    #def reindex():
    #    with app.app_context():
    #       whooshee.reindex()



    @app.cli.command()
    def routes():
        """'Display registered routes"""
        rules = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            rules.append((rule.endpoint, methods, str(rule)))

        sort_by_rule = operator.itemgetter(2)
        for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
            route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
            print(route)


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        '''Shut Down Session'''
        if exception:
            db.session.rollback()
        db.session.close()
        db.session.remove()
 
    @app.teardown_request
    def teardown_request(exception):
        '''Teardown Request'''
        if exception:
            db.session.rollback()
        db.session.remove()
 
 
    app.logger.setLevel(logging.NOTSET)

    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(
            req.method, req.url, req.data, resp)
        )
        return resp
    return app













