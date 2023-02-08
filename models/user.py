from db import db
import os

class UserModel(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_warnings = db.relationship('UserWarningModel', backref='UserModel')

    def __init__(self, username, email):
        self.username = username
        self.email = email
    
    def json(self):
        return {
            'id':self.id,
            'username': self.username,
            'email': self.email,
        }
    
    @classmethod    
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def check_if_user_exists(self, user):
        if self.find_by_username(user['username']) or self.find_by_email(user['email']):
            return True
        return False
    
    @classmethod    
    def find_by_id(cls, _id):
       return cls.query.filter_by(id=_id).first()

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

