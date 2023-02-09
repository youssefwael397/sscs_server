from playsound import playsound
import face_recognition
from flask import Response
from keras.models import load_model
# from date_funcs import current_datetime
from models.warning import WarningModel
from faceRecThread import FaceRecognition
import numpy as np
import os
import glob
import cv2
import time
import uuid

model = load_model('utils/violence_model.h5')
print("loading model")
warning_path = "static/warnings/"


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


def open_cam():
    vc = cv2.VideoCapture(0)

    while True:
        ret, frame = vc.read()
        if not ret:
            break
        cv2.imshow('video stream', frame)
        k = cv2.waitKey(1)
        if ord('q') == k:
            break

    # close the video capture
    cv2.destroyAllWindows()
    vc.release()


def get_detected_name(results, names):
    max_length = 0
    length = 0
    last_true_index = None

    print("results:", results)
    for i in range(len(results)):
        if results[i] == True:
            length += 1
            # max_length += 1

            if results[i-1] == True:
                last_true_index = i

            if last_true_index == i-1:
                max_length += 1
        else:
            if length > max_length:
                max_length = length
            length = 0

    if last_true_index is None:
        return "Unknown"
    else:
        first_true_index = last_true_index - (max_length - 1)
        if first_true_index == last_true_index:
            median_index = first_true_index
        else:
            median_index = (first_true_index + last_true_index) / 2
            median_index = round(median_index) - 1
        print("max_length: ", max_length)
        print("first_true_index: ", first_true_index)
        print("last_true_index: ", last_true_index)
        print("median_index: ", median_index)
        print("names[median_index]: ", names[median_index])
        return names[round(median_index)]


def testRTC(socketio):
    vc = cv2.VideoCapture(0)

    while True:
        ret, frame = vc.read()
        if not ret:
            break
        socketio.emit('rtc', {'name': 'pyramids'})


def open_RTC(faces, names, socketio):
    vc = cv2.VideoCapture(0)
    camera = vc
    print('open_RTC')

    while True:
        ret, frame1 = vc.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        detected_faces = face_recognition.face_locations(frame_rgb)

        for detected_face in detected_faces:
            top, right, bottom, left = detected_face
            cv2.rectangle(frame1, (left, top), (right, bottom), (255, 0, 0), 2)
            encoding = face_recognition.face_encodings(
                frame_rgb, [detected_face])[0]

            results = face_recognition.compare_faces(faces, encoding)

            name = 'Unknown'
            face_distance = face_recognition.face_distance(faces, encoding)
            best_match_index = np.argmin(face_distance)

            if results[best_match_index]:
                name = names[best_match_index]

            # print(name)
            cv2.putText(frame1, name, (left, bottom + 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        frame = cv2.imencode('.jpg', frame1)[1]
        frame = frame.tobytes()

        # print('message received!!!')
        # print(frame)

        socketio.emit('rtc', frame)
        socketio.sleep(0)


def open_RTC_violence(socketio):

    max_v = 5
    v_count = 0
    frames_list = []
    start_time = None
    vc = cv2.VideoCapture(0)
    isRecording = False
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_number = 0
    while True:
        ret, frame = vc.read()
        frame_number += 1
        if not ret:
            break
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (128, 128)).astype("float32")
        img = img.reshape(128, 128, 3) / 255
        predictions = model.predict(np.expand_dims(img, axis=0), verbose=0)
        preds = predictions > 0.5

        if len(frames_list) < 5:
            frames_list.append(preds[0][0])
        else:
            frames_list.pop(0)
            frames_list.append(preds[0][0])

        if preds and v_count != max_v:
            v_count += 1

            # if not isRecording and max_v == v_count:
            #     vid_uuid = uuid.uuid4()
            #     vid_path = f'{warning_path}{vid_uuid}.mp4'
            #     print(vid_uuid)
            # data = {
            #     "date": f"{current_datetime()}",
            #     "status": "Violence",
            #     "video_name": f"{vid_uuid}.mp4",
            #     "user_warnings": ""
            # }
            # print(data)
            # warn = WarningModel(**data)

            # try:
            #     warn.save_to_db()
            # except:
            #     print("Error saving warning to db")

            # for playing wav file
            # playsound('/static/others/alarm-car-or-home.wav')
            # print('playing sound using  playsound')

            if not isRecording and max_v == v_count:

                vid_uuid = uuid.uuid4()
                vid_path = f'{warning_path}{vid_uuid}.mp4'
                print(vid_uuid)
                # save the detected violence video to /static/warnings/
                writer = cv2.VideoWriter(
                    vid_path, cv2.VideoWriter_fourcc(*'DIVX'), 20, (width, height))
                # implement face detection and recognition for saved video 
                FR_thread = FaceRecognition(f'{vid_path}')

                start_time = time.time()
                isRecording = True

            if isRecording:
                if time.time() - start_time > 10:
                    print(frames_list)
                    if np.sum(frames_list) > 1:
                        start_time = time.time()
                        writer.write(frame)
                else:
                    writer.release()
                    v_count = 0
                    isRecording = False
                    FR_thread.start()

            else:
                writer.write(frame)

        cv2.putText(frame, f'Violence : {preds[0][0]}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, 2)
        # cv2.imshow('video stream', frame)

        frame = cv2.imencode('.jpg', frame)[1]
        frame = frame.tobytes()
        socketio.emit('rtc', frame)
        socketio.sleep(0)

        k = cv2.waitKey(1)
        if ord('q') == k:
            break


def open_face_detect_cam(faces, names):
    vc = cv2.VideoCapture(0)

    while True:
        ret, frame = vc.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detected_faces = face_recognition.face_locations(frame_rgb)

        for detected_face in detected_faces:
            top, right, bottom, left = detected_face
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            encoding = face_recognition.face_encodings(
                frame_rgb, [detected_face])[0]

            results = face_recognition.compare_faces(faces, encoding)

            name = 'Unknown'
            face_distance = face_recognition.face_distance(faces, encoding)
            best_match_index = np.argmin(face_distance)

            if results[best_match_index]:
                name = names[best_match_index]

            cv2.putText(frame, name, (left, bottom + 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.imshow('video stream', frame)
        k = cv2.waitKey(1)
        if ord('q') == k:
            break

    # close the video capture
    cv2.destroyAllWindows()
    vc.release()


def count_faces_from_video(video_path, faces, known_names):
    vc = cv2.VideoCapture(video_path)
    names = []
    count = 0

    while True:
        ret, frame = vc.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detected_faces = face_recognition.face_locations(frame_rgb)

        for detected_face in detected_faces:
            top, right, bottom, left = detected_face
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            encoding = face_recognition.face_encodings(
                frame_rgb, [detected_face])[0]

            results = face_recognition.compare_faces(faces, encoding)

            name = 'Unknown'
            face_distance = face_recognition.face_distance(faces, encoding)
            best_match_index = np.argmin(face_distance)

            if results[best_match_index]:
                name = known_names[best_match_index]

            is_exists = False
            for n in names:
                if n == name:
                    is_exists = True

            if not is_exists:
                names.append(name)
                count = count + 1

            # cv2.putText(frame, name, (left, bottom + 25),
            #             cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # cv2.imshow('video stream', frame)
        # k = cv2.waitKey(1)
        # if ord('q') == k:
        #     break

    # close the video capture
    # cv2.destroyAllWindows()
    vc.release()

    return names, count


# how to implement face recognition
# frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
#        detected_faces = face_recognition.face_locations(frame_rgb)

#         for detected_face in detected_faces:
#             top, right, bottom, left = detected_face
#             cv2.rectangle(frame1, (left, top), (right, bottom), (255, 0, 0), 2)
#             encoding = face_recognition.face_encodings(
#                 frame_rgb, [detected_face])[0]

#             results = face_recognition.compare_faces(faces, encoding)

#             name = 'Unknown'
#             face_distance = face_recognition.face_distance(faces, encoding)
#             best_match_index = np.argmin(face_distance)

#             if results[best_match_index]:
#                 name = names[best_match_index]

#             # print(name)
#             cv2.putText(frame1, name, (left, bottom + 25),
#                         cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

#         frame = cv2.imencode('.jpg', frame1)[1]
#         frame = frame.tobytes()

#         # print('message received!!!')
#         # print(frame)

#         socketio.emit('rtc', frame)
#         socketio.sleep(0)
