from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import InputRequired
from wtforms_alchemy import model_form_factory
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from app.models import TrackerCategory
from app.utils import db

BaseModelForm = model_form_factory(FlaskForm)





class TrackerForm(BaseModelForm):
    title = StringField('Title of Tracker', validators=[InputRequired()])
    #tracker_type = SelectField('Type of Tracker', validators=[InputRequired()], choices=[
     
    #])
    timestamp = IntegerField('Validity period of tracker in minutes', validators=[InputRequired()])
    description = TextAreaField(u'Descripe this activity')      
    categories = QuerySelectField(
        'Categories',
        validators=[InputRequired()],
        get_label='title',
        query_factory=lambda: db.session.query(TrackerCategory).all())
    
                             
class CategoryForm(FlaskForm):
    title = StringField('Category title')
    description = TextAreaField('category description')
    




