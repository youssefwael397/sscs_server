import threading
import cv2
import glob
import os
import face_recognition
import uuid
import numpy as np
from models.user import UserModel
from models.warning import WarningModel
from models.user_warning import UserWarningModel


def get_faces_paths_and_names(images_path):
    names = []
    faces_paths = []

    for name in os.listdir(images_path):
        images_mask = '%s%s/*.jpg' % (images_path, name)
        images_paths = glob.glob(images_mask)
        faces_paths += images_paths
        names += [name for x in images_paths]

    return names, faces_paths


def get_face_encodings(img_path):
    image = face_recognition.load_image_file(img_path)
    encoding = face_recognition.face_encodings(image)
    # print("encoding: " , encoding)
    return encoding[0]


def get_faces(faces_paths):
    # faces = []
    faces = [get_face_encodings(img_path) for img_path in faces_paths]
    return faces


def FaceRecognition(file_name):  # threading.Thread
        print("Running Face Recognition to save user warning")
        registered_faces_path = 'static/users/'
        warning_path = "static/warnings/"

        names, faces_paths = get_faces_paths_and_names(registered_faces_path)
        faces = get_faces(faces_paths)

        vc = cv2.VideoCapture(f'{warning_path}{file_name}')
        print("start FaceRecognition video capture")

        while True:
            print('inside video capture')
            ret, frame = vc.read()
            if not ret:
                break
            # face recogniton code and save users in video if found
            while True:
                ret, frame = vc.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                detected_faces = face_recognition.face_locations(frame_rgb)
                print("detected_faces: ", detected_faces)

                for detected_face in detected_faces:
                    top, right, bottom, left = detected_face
                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), (255, 0, 0), 2)
                    encoding = face_recognition.face_encodings(
                        frame_rgb, [detected_face])[0]

                    results = face_recognition.compare_faces(faces, encoding)

                    name = 'Unknown'
                    face_distance = face_recognition.face_distance(
                        faces, encoding)
                    best_match_index = np.argmin(face_distance)

                    if results[best_match_index]:
                        name = names[best_match_index]

                    # print(name)
                    print("name: ", name)

                    if name == 'Unknown':
                        # save unknown face in db
                        new_uuid = uuid.uuid4()
                        name = f"unknown_{new_uuid}"
                        print('unknown face folder')
                        os.mkdir(f'static/users/{name}')
                        cv2.imwrite(f'static/users/{name}/{new_uuid}.jpg', frame)
                        print("unknown new name: ", name)

                        data = {
                            "username": name,
                            "email": f"unknown_{new_uuid}@gmail.com",
                        }
                        
                        new_user = UserModel(**data)

                        try:
                            new_user.save_to_db()
                            print("New unknown user saved")

                        except Exception as e:
                            print(f"Error saving {e}")

                    # insert user_id and warning_id to user_warnings
                    warn_id = 0
                    user_id = 0
                    user = UserModel.find_by_name(name)
                    warn_exists = WarningModel.find_by_video_name(file_name)
                    if warn_exists:
                        warn_id = warn_exists.id
                    if user:
                        user_id = user.id

                    data = {
                        "user_id": user_id,
                        "warning_id": warn_id,
                    }

                    print("user warning data: ", data)

                    user_warn = UserWarningModel.checkDuplicate(
                        user_id, warn_id)
                    
                    if user_warn:
                        print("Duplicated user warning")
                    else: 
                        user_warn = UserWarningModel(**data)
                        try:
                            user_warn.save_to_db()
                            print("user_warn.save_to_db successfully saved")
                        except:
                            print("error user_warn.save_to_db faceRecThread.py :138")

                    
        # close the video capture
        vc.release()