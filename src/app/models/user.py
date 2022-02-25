import datetime
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin, current_user
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedSerializer as Serializer
from config import Config
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils import db, login_manager



class Permission:
    GENERAL = 'GENERAL'
    ADMINISTER = 'ADMINISTRATOR'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    index = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    access_role = db.Column(db.String(70), unique=True)
    
    
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.GENERAL, 'main', True),
            'Administrator': (
                Permission.ADMINISTER,
                'admin',
                False  # grants all permissions
            )
        }
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.access_role = roles[r][0]
            role.index = roles[r][1]
            role.default = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role \'%s\'>' % self.name

    




class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    gender = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True)
    area_code = db.Column(db.String(6), index=True)
    mobile_phone = db.Column(db.BigInteger, unique=True, index=True)
    summary_text = db.Column(db.Text)
    city = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    country = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete="CASCADE"))
    trackers = db.relationship('Tracker', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.date.today())
    updated_at = db.Column(db.DateTime, default=datetime.date.today())
   
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == Config.ADMIN_EMAIL:
                self.role = Role.query.filter_by(
                    permissions=Permission.ADMINISTER).first()
                print(self.role)    
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

   

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name   

    @property
    def created_day(self):
        return self.created_at.date()
    
    def can(self, access):
        return self.role is not None and self.role.access_role == access or self.role.access_role == Permission.ADMINISTER
    
    def is_admin(self):
        return self.can(Permission.ADMINISTER)
        

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_confirmation_token(self, expiration=604800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return str(s.dumps({'confirm': self.id}).decode())



    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def generate_password_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return str(s.dumps({'reset': self.id}).decode())

    def confirm_account(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password_hash = generate_password_hash(new_password)
        db.session.add(self)
        db.session.commit()
        return True

    @staticmethod
    def generate_fake(count=100, **kwargs):
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker

        fake = Faker()
        roles = Role.query.all()
        if len(roles) <= 0:
            Role.insert_roles()
            roles = Role.query.all()

        seed()
        for i in range(count):
            u = User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                city=fake.city(),
                state=fake.state(),
                summary_text=fake.text(),
                password='password',
                confirmed=True,
                role=choice(roles),
                **kwargs)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    


    def __repr__(self):
        return '<User \'%s\'>' % self.full_name            

class AnonymousUser(AnonymousUserMixin):
    def can(self):
        return False

    def is_admin(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))             


login_manager.anonymous_user = AnonymousUser           

   

