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
    print(categories)
    categories_count = TrackerCategory.query.count()
    return render_template('pages/home.html', active=active_trackers, archived = archived_trackers, categories=categories, categories_count=categories_count)

@main.route('/tracker/<int:tracker_id>/<tracker_title>/')
@login_required
def view_tracker(tracker_id, tracker_title):
    obj = Tracker.query.filter_by(user=current_user).filter_by(id=tracker_id).filter_by(title=tracker_title).first_or_404()
    return render_template('pages/tracker_detail.html', obj=obj)    

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
    tracker = Tracker.query.filter_by(user=current_user).get_or_404(tracker_id)
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
            return redirect(url_for('main.view_tacker', tracker_id=tracker.id, tracker_title=tracker.title))
        return render_template('pages/tracker-add-edit.html', tracker=tracker, form=form)    
            


@main.route('/tracker/<int:tracker_id>/<tracker_type>/<tracker_title>/_delete')
@login_required
def delete_tracker(tracker_id, tracker_type, tracker_title):
    obj = Tracker.query.filter_by(user=current_user).filter_by(id=tracker_id).\
        filter_by(tracker_type=tracker_type).filter_by(title=tracker_title).get_or_404()
    db.session.delete(obj)
    db.session.commit()
    flash('Tracker successfully deleted, feel free to create more', 'success')
    return redirect(url_for('main.index'))






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
