from flask import render_template
from . import public



################
#### routes ####
################


@public.route('/')
def index():
    return render_template('pages/index.html')


@public.route('/about')
def about():
    return render_template('pages/placeholder.about.html')