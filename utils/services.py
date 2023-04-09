# from flask import Response, current_app
from utils.date_funcs import current_datetime
from factory import create_app
from models.warning import WarningModel


def create_warning_video(filename):
    data = {
        "date": f"{current_datetime()}",
        "status": "Violence",
        "video_name": f"{filename}.mp4",
    }

    app = create_app()

    with app.app_context():
        warn = WarningModel(**data)
        try:
            warn.save_to_db()
            print("warning saved to db")
        except:
            print("Error saving warning to db")
    