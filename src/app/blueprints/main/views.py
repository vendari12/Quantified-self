from flask import flash, url_for, redirect, request, render_template
from flask_login import login_required, current_user

from app.blueprints.main.forms import TrackerForm, CategoryForm
from . import main
from app.models import Tracker, TrackerCategory
from app.utils import db
from app.decorator import admin_required

@main.route('/', methods=['GET'])
@login_required
def index():
    active_trackers = Tracker.query.filter_by(active=True).all()
    archived_trackers = Tracker.query.filter_by(active=False).all()
    categories = TrackerCategory.query.all()
    categories_count = TrackerCategory.query.count()
    return render_template('pages/home.html', active=active_trackers, archived = archived_trackers, categories=categories, categories_count=categories_count)


@main.route('/trackers/<int:page>', methods=['GET'])
@main.route('/trackers/', defaults={'page': 1}, methods=['GET'])
@login_required
def trackers(page):    
    trackers = Tracker.query.filter_by(user=current_user).order_by(Tracker.created_at.desc()).paginate(page, per_page=50)
    categories = TrackerCategory.query.all()
    categories_count = TrackerCategory.query.count()
    return render_template('pages/trackers.html',  archived = trackers, categories=categories, categories_count=categories_count)



@main.route('/tracker/<int:tracker_id>/<tracker_title>/')
@login_required
def view_tracker(tracker_id, tracker_title):
    obj = Tracker.query.filter_by(user=current_user).filter_by(id=tracker_id).filter_by(title=tracker_title).first_or_404()
    latest = Tracker.query.filter_by(user=current_user).order_by(Tracker.created_at.desc()).all()[:5]
    categories = TrackerCategory.query.all()
    return render_template('pages/tracker_detail.html', obj=obj, categories=categories, latest=latest)    

@main.route('/tracker/add', methods=['GET','POST'])
@login_required
def create_tracker():
    form = TrackerForm()
    if form.validate_on_submit():
        tracker_obj = Tracker(
            title = form.title.data,
            category = form.categories.data,
            description = form.description.data,
            timestamp = form.timestamp.data,
            user = current_user
        )
        db.session.add(tracker_obj)
        db.session.commit()
        flash(f'You have successfully created a tracker, it will expire in {form.timestamp.data} minutes')
        return redirect(url_for('main.view_tracker', tracker_id=tracker_obj.id, tracker_title=tracker_obj.title))
    return render_template('pages/tracker-add-edit.html', form=form) 

@main.route('/tracker/<int:tracker_id>/<tracker_title>/_edit', methods=['GET', 'POST'])
@login_required
def edit_tracker(tracker_id, tracker_title):
    tracker = Tracker.query.filter_by(user=current_user).first_or_404(tracker_id)
    form = TrackerForm(obj=tracker)
    if request.method == 'POST':
        if form.validate_on_submit():
            tracker.title = form.title.data
            tracker.timestamp = form.timestamp.data
            tracker.description = form.description.data
            tracker.category = form.categories.data
            db.session.add(tracker)
            db.session.commit()
            flash(f'You have successfully Edited this tracker, it will now expire in {form.timestamp.data} minutes')
            return redirect(url_for('main.view_tracker', tracker_id=tracker.id, tracker_title=tracker.title))
    return render_template('pages/tracker-add-edit.html', tracker=tracker, form=form)    
            


@main.route('/tracker/<int:tracker_id>/<tracker_title>/_delete')
@login_required
def delete_tracker(tracker_id,tracker_title):
    obj = Tracker.query.filter_by(user=current_user).filter_by(id=tracker_id).\
        filter_by(title=tracker_title).first_or_404()
    db.session.delete(obj)
    db.session.commit()
    flash('Tracker successfully deleted, feel free to create more', 'success')
    return redirect(url_for('main.tracker'))






#Tracker Categories


@main.route('/tracker/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def tracker_category_create():
    form = CategoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cat = TrackerCategory(
                title=form.title.data,
                description=form.description.data,
                )
            db.session.add(cat)
            db.session.commit()
            flash('Category {} successfully created'.format(cat.title), 'success')
            return redirect(url_for('main.index'))
    return render_template('pages/category-add-edit.html', form=form)


@main.route('/tracker/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def tracker_category_edit(category_id):
    category = TrackerCategory.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if request.method == 'POST':
        if form.validate_on_submit():
            category.title = form.title.data
            category.description = form.description.data
            db.session.add(category)
            db.session.commit()
            flash('Category {} successfully Updated'.format(category.name), 'success')
            return redirect(url_for('main.index'))
    return render_template('pages/categories/add-edit.html', form=form, category=category)


@main.route('/tracker/categories/<int:category_id>/_delete', methods=['POST'])
@login_required
@admin_required
def tracker_category_delete(category_id):
    cat = TrackerCategory.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Category.', 'success')
    return redirect(url_for('main.index'))



@main.route('/category/<int:category_id>/<int:page>', methods=['GET'])
@main.route('/category/<int:category_id>', defaults={'page': 1}, methods=['GET'])
@login_required
def main_category(category_id, page):
    category = TrackerCategory.query.get(category_id)
    posts = Tracker.query.filter(Tracker.category.has(id=category.id)).order_by(Tracker.created_at.desc()).paginate(page, per_page=40)
    if category and posts:
        return render_template('pages/category-detail.html',posts=posts, category=category)
   


@main.route('/category/<int:page>', methods=['GET'])
@main.route('/category/', defaults={'page': 1}, methods=['GET'])
def categories(page):
    category = TrackerCategory.query.paginate(page, per_page=50)
    return render_template('pages/category.html',categories=category)   

"""
@main.route('/tracker/<int:tracker_id>/comment', methods=['POST'])
@login_required
def add_comment(tracker_id):

    post = Tracker.query.get_or_404(tracker_id)

    data = request.get_json(force = True)
    text = data['text']

    if not text:

        return dict(status='fail', message='text required'), 400

    parent_id = data['parent_id']

    if parent_id and parent_id != '0' and parent_id != 0:

        comment = mainComment(

            post_id=post.id,

            text=text,

            user_id=current_user.id,

            parent_id=parent_id

        )

    else:

        comment = mainComment(

            post_id=post.id,

            text=text,

            user_id=current_user.id,

        )

    db.session.add(comment)

    db.session.commit()

    return dict(status='sucess', message="comment added successfuly"), 201
"""


