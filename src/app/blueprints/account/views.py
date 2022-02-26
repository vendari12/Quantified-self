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
                flash('Invalid email or password.', 'danger')
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





@account.route('/reset-password', methods=['GET', 'POST'])
def forgot():
    """Respond to existing user's request to reset their password."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = url_for('account.reset_password', token=token, _external=True)
            print(reset_link)   
        flash('A password reset link has been sent to {}.'.format(user.email), 'warning')
        return redirect(url_for('account.login'))
    return render_template('account/forgot.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid phone number.', 'form-error')
            return redirect(url_for('post.post_create'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'danger')
            return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('account.login'))
        else:
            flash('Original password is invalid.', 'danger')
    return render_template('account/manage.html', form=form)



@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            data = {'change_email': change_email_link,
                    'user': current_user._get_current_object()}
            """get_queue().enqueue(
                send_email,
                recipient=new_email,
                subject='Confirm Your New Email',
                template='account/email/change_email',
                # current_user is a LocalProxy, we want the underlying user
                # object
                body = data)"""
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('post.post_create'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('post.post_create'))






@account.route('/manage/update-profile', methods=['GET', 'POST'])
@login_required
def change_profile_details():
    """Respond to existing user's request to change their profile details."""
    user_instance = current_user
    form = EditProfileForm(obj=user_instance)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                form.populate_obj(user_instance)
                db.session.add(user_instance)
                if request.files['photo']:
                    image_filename = images.save(request.files['photo'])
                    image_url = images.url(image_filename)
                    picture_photo = Photo.query.filter_by(user_id=current_user.id).first()
                    if not picture_photo:
                        picture_photo = Photo(
                            image_filename=image_filename,
                            image_url=image_url,
                            user_id=current_user.id,
                        )
                    else:
                        picture_photo.image_filename = image_filename
                        picture_photo.image_url = image_url
                    db.session.add(picture_photo)
                db.session.commit()
                flash('You have successfully updated your profile',
                      'success')
                return redirect(url_for('account.manage'))
            else:
                flash('Unsuccessful.', 'warning')
    return render_template('account/edit_profile.html', form=form)