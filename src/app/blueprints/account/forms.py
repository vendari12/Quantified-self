from flask import url_for
from flask_wtf import Form
from wtforms import StringField, PasswordField, EmailField, ValidationError, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired, Email
from app.models import User
from wtforms_alchemy import model_form_factory
from flask_wtf import FlaskForm

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


class RequestResetPasswordForm(Form):
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


class CreatePasswordForm(Form):
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



