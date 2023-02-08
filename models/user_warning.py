from db import db
import os


class UserWarningModel(db.Model):
    __tablename__ = 'user_warnings'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    warning_id = db.Column(db.Integer, db.ForeignKey('warnings.id'))

    def __init__(self, user_id, warning_id):
        self.date = user_id
        self.status = warning_id

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warning_id': self.warning_id,
        }


    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).all()

    @classmethod
    def find_by_user_id(cls, _id):
        return cls.query.filter_by(user_id=_id).all()

    @classmethod
    def find_by_warning_id(cls, _id):
        return cls.query.filter_by(warning_id=_id).all()

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
