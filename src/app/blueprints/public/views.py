from flask import render_template
from . import public
from app.models.tracker import TrackerCategory



################
#### routes ####
################


@public.route('/')
def index():
    categories = TrackerCategory.query.all()
    return render_template('pages/index.html', categories=categories)


@public.route('/about')
def about():
    categories = TrackerCategory.query.all()
    return render_template('pages/about.html', categories=categories)






"""@public.route('/sub', methods=['POST'])
def subscribe():
    data = request.get_json(force=True)
    email = data['email']
    if NewsLetter.query.filter_by(email=email).first():

        return dict(status='invaild', message='already subscribed to newsletter')
    sub = NewsLetter(

        email=email,
    )
    db.session.add(sub)
    db.session.commit()
    return dict(status='success', message="successfully subscried to newsletter")""" 