from flask_restful import Resource, reqparse
from models.user_warning import UserWarningModel
from utils.file_handler import  save_logo, delete_logo, delete_file

class UserWarnings(Resource):
    def get(self):
        return {"user_warnings": [user_warning.json() for user_warning in UserWarningModel.find_all()]}

class UserWarning(Resource):
    @classmethod
    def delete(cls, user_warning_id):
        user_warning = UserWarningModel.find_by_id(user_warning_id)
        if not user_warning:
            return {"message": "Warning not found."}, 404
        try:
            user_warning.delete_from_db()
        except:
            return {"message": "An error occurred while deleting the user from this warning."}, 500

        return {"message": "User Deleted from this warning successfully."}, 201


class UserWarningByUser(Resource):
    @classmethod
    def get(cls, user_id):
        Warnings = UserWarningModel.find_by_user_id(user_id)
        if Warnings:
            return Warnings.json()
        return {"message": "This user don't have any violence actions."}, 404
