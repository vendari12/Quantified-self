import os, sys, datetime


basedir = os.path.abspath(os.path.dirname(__file__))


PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 3:
    import urllib.parse

class Config:
    APP_NAME = os.environ.get('APP_NAME') or "Quantified-self"

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    
    
    
    

    # Admin account
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Password'
    ADMIN_MOBILE_PHONE='00000000'
    ADMIN_AREA_CODE='+44'
    ADMIN_EMAIL = os.environ.get(
        'ADMIN_EMAIL') or 'quantifiedself@gmail.com'

    REDIS_URL = os.getenv('REDISTOGO_URL') or 'http://localhost:6379'
   
    
    # Parse the REDIS_URL to set RQ config variables
    if PYTHON_VERSION == 3:
        urllib.parse.uses_netloc.append('redis')
        url = urllib.parse.urlparse(REDIS_URL)


    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0
    

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_FILE_MAX_AGE_DEFAULT = datetime.timedelta(days=365)
    UPLOADED_IMAGES_DEST = '/home/ubuntu/networkedng/flask-base/app/static/photo/' if \
        not os.environ.get('UPLOADED_IMAGES_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_IMAGES_DEST')
    UPLOADED_DOCS_DEST = '/home/ubuntu/networkedng/flask-base/app/static/docs/' if \
        not os.environ.get('UPLOADED_DOCS_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_DOCS_DEST')
    docs = UPLOADED_DOCS_DEST
    UPLOADED_PATH = os.path.join(basedir, 'uploads')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI= "sqlite:///database.db"

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN TESTING MODE.  \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///database.db"
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
     #   'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET'



class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'unix': UnixConfig
}
