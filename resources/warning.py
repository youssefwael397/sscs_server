from flask_restful import Resource, reqparse
from models.warning import WarningModel
from utils.file_handler import save_logo, delete_logo, delete_file
from flask import send_from_directory
from utils.date_funcs import current_datetime
from factory import create_app
# from resources.stream import create_warning_video

class Warnings(Resource):
    def get(self):
        return {"warnings": [warning.json() for warning in WarningModel.find_all()]}


class Warning(Resource):
    @classmethod
    def get(cls, warning_id):
        Warning = WarningModel.find_by_id(warning_id)
        if Warning:
            return Warning.json()
        return {"message": "Warning not found."}, 404

    @classmethod
    def delete(cls, warning_id):
        warning = WarningModel.find_by_id(warning_id)
        if not warning:
            return {"message": "Warning not found."}, 404
        try:
            warning.delete_from_db()
            delete_file(warning.video_name, 'static/warnings')
        except:
            return {"message": "An error occurred while deleting the warning."}, 500

        return {"message": "Warning Deleted successfully."}, 201

class WarningsVideo(Resource):
    def get(self, filename):
        app = create_app()
        with app.app_context():
            print(filename)     
            return send_from_directory(app.config['VIDEO_FOLDER'], filename)


# class CreateWarning(Resource):
#     @classmethod
#     def post(cls):
#         create_warning_video()
#         return {"message": "Warning Created Successfully."} 