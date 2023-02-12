from db import db
import os



class WarningModel(db.Model):
    __tablename__ = 'warnings'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(255), unique=False, nullable=False)
    video_name = db.Column(db.String(255), unique=True, nullable=False)
    user_warnings = db.relationship('UserWarningModel', backref='WarningModel')


    def __init__(self, date, status, video_name):
        self.date = date
        self.status = status
        self.video_name = video_name

    def json(self):
        return {
            'id': self.id,
            'date': self.date,
            'status': self.status,
            'video_name': self.video_name,
        }

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_video_name(cls, _video_name):
        return cls.query.filter_by(video_name=_video_name).first()
    
    @classmethod
    def find_by_date(cls, date):
        return cls.query.filter_by(date=date).first()
    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        # SQL_ALCHEMY automatically checks if the data is changed, so takes care of both insert
        # and update
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
