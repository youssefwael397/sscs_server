from db import db
from models.warning import WarningModel
from models.user import UserModel
from flask import jsonify

class UserWarningModel(db.Model):
    _tablename_ = 'user_warnings'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    warning_id = db.Column(db.Integer, db.ForeignKey('warnings.id'))

    def _init_(self, user_id, warning_id):
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
    def checkDuplicate(cls, _user_id, _warning_id):
        return cls.query.filter_by(user_id=_user_id, warning_id=_warning_id).all()

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


    def get_warnings_by_user_id(user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_warnings = UserWarningModel.query.filter_by(user_id=user.id).all()

        warning_details = []

        for user_warning in user_warnings:
            warning = WarningModel.query.filter_by(id=user_warning.warning_id).first()

            warning_info = {
                'id': warning.id,
                'date': warning.date,
                'status': warning.status,
                'video_name': warning.video_name
            }
            warning_details.append(warning_info)

        return jsonify(warning_details)


    def get_users_by_warning_id(warning_id):
        warning = WarningModel.query.filter_by(id=warning_id).first()

        if not warning:
            return jsonify({'error': 'Warning not found'}), 404

        warning_users = UserWarningModel.query.filter_by(warning_id=warning.id).all()

        user_details = []

        for warning_user in warning_users:
            user = UserModel.query.filter_by(id=warning_user.user_id).first()

            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            user_details.append(user_dict)
        return jsonify(user_details)