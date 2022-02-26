from wtforms import StringField, PasswordField, EmailField, ValidationError\
    , SelectField, BooleanField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, Email
from app.models import User
from flask_uploads import UploadSet, IMAGES
from wtforms_alchemy import model_form_factory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Optional
from wtforms_alchemy import Unique


images = UploadSet('images', IMAGES)

BaseModelForm = model_form_factory(FlaskForm)





class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('Keep me logged in')





class RegistrationForm(BaseModelForm):
    first_name = StringField('First name', validators=[InputRequired()])
    last_name = StringField('Last name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    gender = SelectField(u'Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    username = StringField(u'Username', validators=[InputRequired()])      
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('confirm', 'Passwords must match')
        ])
    confirm = PasswordField('Confirm password', validators=[InputRequired()])
    

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')                             


class RequestResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])


class ResetPasswordForm(BaseModelForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])




class ChangeEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    password = PasswordField('Password', validators=[InputRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')




class EditProfileForm(BaseModelForm):
    first_name = StringField('First name', validators=[InputRequired()])
    last_name = StringField('Last name', validators=[InputRequired()])
    photo = FileField('Profile Image', validators=[Optional(), FileAllowed(images, 'Images only!')])
    area_code = StringField('Phone area code only')
    mobile_phone = IntegerField('Phone numbers only', validators=[InputRequired(), Unique(User.mobile_phone)])
    city = StringField('City', validators=[InputRequired()])
    state = SelectField(u'Select State in Nigeria')
    gender = SelectField(u'Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    country = StringField('Select Country')
      
    zip = StringField('Zip Code', validators=[InputRequired(), Length(1, 7)])
    summary_text = TextAreaField('Summary Text or Description')
    
