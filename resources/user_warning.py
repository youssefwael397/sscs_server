from flask_restful import Resource, reqparse
from models.user_warning import UserWarningModel
from models.warning import WarningModel
from utils.faceRecThread import FaceRecognition
from utils.file_handler import save_logo, delete_logo, delete_file


class UserWarnings(Resource):
    def get(self):
        return {"user_warnings": [user_warning.json() for user_warning in UserWarningModel.find_all()]}

class WarningByUserId(Resource):
    def get(self , user_id):
        return UserWarningModel.get_warnings_by_user_id(user_id)

class UsersByWarningId(Resource):
    def get(self , warning_id):
        warning = WarningModel.find_by_id(warning_id)
        if not warning: 
            return {'message': 'Warning not found'}, 404
        return UserWarningModel.get_users_by_warning_id(warning_id)

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
        user_warnings = UserWarningModel.find_by_user_id(user_id)
        if user_warnings:
            return user_warnings.json()
        return {"message": "This user don't have any violence actions."}, 404


class WarningExtractFaces(Resource):
    @classmethod
    def get(cls, warning_id):
        Warning = WarningModel.find_by_id(warning_id)
        if Warning:
            print("video name: ", Warning.video_name)
            FR = FaceRecognition(Warning.video_name)
            print(FR)
        return {"user_warnings": [user_warning.json() for user_warning in UserWarningModel.find_by_warning_id(warning_id)]}