import threading
import cv2
import face_recognition
from face_detect import get_faces_paths_and_names, get_faces
import numpy as np


class FaceRecognition(threading.Thread):
    def __init__(self, file_name):
        threading.Thread.__init__(self)
        self.file_name = file_name

    def run(self):
        registered_faces_path = 'static/users/'
        names, faces_paths = get_faces_paths_and_names(registered_faces_path)
        faces = get_faces(faces_paths)

        vc = cv2.VideoCapture(f'{self.file_name}')

        while True:
            ret, frame = vc.read()
            if not ret:
                break
            # face recogniton code and save users in video if found
            #
            #
            while True:
                ret, frame = vc.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                detected_faces = face_recognition.face_locations(frame_rgb)

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

                    print(name)
                    

            # close the video capture
            vc.release()
