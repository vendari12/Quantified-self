#!/usr/bin/python3
from multiprocessing import managers
import typer, os, subprocess
#from redis import Redis
#from rq import Connection, Queue, Worker
from app import create_app
from app.utils import db
from app.models import *
from config import Config

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


manager = typer.Typer()

@manager.command()
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command()
def create_tables():
    with app.app_context():
        db.create_all()


@manager.command()
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    with app.app_context():
        db.drop_all()
        db.configure_mappers()
        db.create_all()
        db.session.commit()

@manager.command()
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    with app.app_context():
        User.generate_fake(count=number_users)


@manager.command()
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()

@manager.command()
def runserver():
    """Runs the set-up needed for local development."""
    app.run()



@manager.command()
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()

    

def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    with app.app_context():
        Role.insert_roles()
        for role in Role.query.all():
            print(role)
        admin_query = Role.query.filter_by(name='Administrator').first()
        if admin_query is not None:
            if db.session.query(User).filter_by(email=Config.ADMIN_EMAIL).first() is None:   
                user = User(
                    role=admin_query,
                    first_name='Admin',
                    last_name='Account',
                mobile_phone=Config.ADMIN_MOBILE_PHONE,
                area_code=Config.ADMIN_AREA_CODE,
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL)
                db.session.add(user)
                db.session.commit()
                print('Added administrator {}'.format(user.full_name))


#@manager.command
#def run_worker():
    """Initializes a slim rq task queue."""
    """listen = ['default']
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD'])

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()"""


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


  

if __name__ == '__main__':
    manager()
