# from flask import Response, current_app
from utils.date_funcs import current_datetime
from factory import create_app
from models.warning import WarningModel
from models.user_warning import UserWarningModel
from models.user import UserModel
import os
import cv2
import uuid



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
    


def create_user_warning(name, warning_id, frame):
    app = create_app()
    current_name = name
    # if name is not exists in database
    # we will save new user to db 
    # and his photo in static/users
    if name == 'unknown':
        # save unknown face in db
        new_uuid = uuid.uuid4()
        current_name = f"unknown_{new_uuid}"
        # create dir for new unknown user by name
        os.mkdir(f'static/users/{current_name}')
        cv2.imwrite(f'static/users/{current_name}/{new_uuid}.jpg', frame)

        with app.app_context():
            data = {
            "username": current_name,
            "email": f"unknown_{new_uuid}@gmail.com",
            }
        
            new_user = UserModel(**data)
            try:
                new_user.save_to_db()
                print("user saved to db")
            except:
                print("Error saving user to db")
    

    # insert user_id and warning_id to user_warnings
    with app.app_context():
        user = UserModel.find_by_username(current_name)
        print(user)
        user_warn_exist = UserWarningModel.checkDuplicate(user.id,warning_id)
        if not user_warn_exist:
            data = {
                "user_id": user.id,
                "warning_id": warning_id,
            }
            user_warn = UserWarningModel(**data)
            try:
                user_warn.save_to_db()
                print("user warning successfully saved")
            except Exception as e:
                print("error while saving user warning: ", e)


        
    