from datetime import datetime
from app.utils import db
from sqlalchemy import func
from sqlalchemy.orm import backref





class TrackerCategory(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(300), unique=True)
    description = db.Column(db.Text)
    tracker = db.relationship('Tracker', backref='category', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=func.now())

    def get_trackers(self):
        return self.tracker.all()

    
    def get_tracker_count(self):
        return len(self.tracker.all())    

    def __repr__(self):
        return '<TrackerCategory \'%s\'>' % self.title 

  


class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(300))
    description = db.Column(db.Text)
    tracker_type = db.Column(db.String(100), unique=True)
    active = db.Column(db.Boolean, default=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    timestamp = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=func.now())

    @property
    def archive_log(self):
        """This function sets a tracker archives a tracker based on the timestamp"""
        now = datetime.now()
        if now - self.updated_at > datetime.timedelta(minutes=self.timestamp):
            self.active = False
            db.session.add(self)
            db.session.commit()
            return False
        else:
            return True    
    @property
    def is_active(self):
        return self.archive_log()

    def __repr__(self):
        return '<Tracker \'%s\'>' % self.title     





