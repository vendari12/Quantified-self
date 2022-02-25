from flask import render_template, request, make_response, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import *
from . import account
from app.models import *
from app.utils import db



################
#### routes ####
################



@account.route('/login', methods=['GET', 'POST'])
def login():
    next = ''
    if 'next' in request.values:
        next = request.values['next']
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_instance = User.query.filter_by(email=form.email.data).first()
            if user_instance is not None and user_instance.password_hash is not None and \
                    user_instance.verify_password(form.password.data):
                login_user(user_instance, form.remember_me.data)
                if request.form['next'] != '':
                    resp = make_response(redirect(request.form['next']))
                    login_user(user_instance, form.remember_me.data)
                    return resp
                flash('You are now logged in. Welcome back!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Invalid username or password.', 'danger')
    return render_template('account/login.html', form=form, next=next)

@account.route('/register', methods=['GET', 'POST'])
#@anonymous_required
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('account/register.html', form=form)
    else:
       
        if form.validate_on_submit():
            user_instance = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    gender=form.gender.data,
                    username=form.username.data,
                    password=form.password.data)
            db.session.add(user_instance)
            db.session.commit()
               
                #user = User.query.filter(User.id==user_instance.id).first()
                      
            flash(f'Welcome, a token has been sent to {user_instance.email}.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Error! Data was not added.', 'error')
            return render_template('account/register.html', form=form)
        
            


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.index'))


@account.route('/forgot')
def forgot():
    form = RequestResetPasswordForm()
    return render_template('forms/forgot.html', form=form)
