from keras.models import load_model
from models.warning import WarningModel
from utils.date_funcs import current_datetime
from utils.faceRecThread import FaceRecognition #error message
import face_recognition
import numpy as np
import cv2
import time
import uuid

warning_path = "static/warnings/"

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
    model = load_model('utils/violence_model.h5')
    print("loading model")
    max_v = 5
    v_count = 0

    frame_number = 0
    frames_list = []
    start_time = None
    isRecording = False
    vc = cv2.VideoCapture(0)
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

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
        # cv2.imshow('violence' , frame)

        # 1
        if len(frames_list) < 5:
            frames_list.append(preds[0][0])
        # 1
        else:
            frames_list.pop(0)
            frames_list.append(preds[0][0])

        # 1
        if preds and v_count != max_v:
            v_count += 1

        # 1
        if not isRecording and max_v == v_count:
            file_name = uuid.uuid4()
            ct = current_datetime()
            print("file_name: ", file_name)
            print("ct: ", ct)
            # save warning video file to /static/warning
            writer = cv2.VideoWriter(
                f'{warning_path}{file_name}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 10, (width, height))
            print("warning video saved successfully")
            # save the video to warnings table to db
            data = {
            "date": f"{current_datetime()}",
            "status": "Violence",
            "video_name": f"{file_name}.mp4",
            }
            print(data)
            warn = WarningModel(**data)
            print("==========================================================")
            print(warn)
            warn.save_to_db()
            print("Warning Created Successfully.")
            # FR_thread = FaceRecognition(f'{file_name}.mp4,')
            start_time = time.time()
            isRecording = True

        # 1
        if isRecording:
            # 2
            if time.time() - start_time > 10:
                print(frames_list)
                # 3
                if np.sum(frames_list) > 1:
                    start_time = time.time()
                    writer.write(frame)
                # 3
                else:
                    writer.release()
                    v_count = 0
                    isRecording = False
                    # FR_thread.run(ct)
            # 2
            else:
                writer.write(frame)
            
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

            # if not isRecording and max_v == v_count:

            #     vid_uuid = uuid.uuid4()
            #     vid_path = f'{warning_path}{vid_uuid}.mp4'
            #     print(vid_uuid)
            #     # save the detected violence video to /static/warnings/
            #     writer = cv2.VideoWriter(
            #         vid_path, cv2.VideoWriter_fourcc(*'DIVX'), 20, (width, height))
            #     # implement face detection and recognition for saved video
            #     # FR_thread = FaceRecognition(f'{vid_path}')

            #     start_time = time.time()
            #     isRecording = True

            # if isRecording:
            #     if time.time() - start_time > 10:
            #         print(frames_list)
            #         if np.sum(frames_list) > 1:
            #             start_time = time.time()
            #             writer.write(frame)
            #     else:
            #         writer.release()
            #         v_count = 0
            #         isRecording = False
            #         # FR_thread.start()
            # else:
            #     writer.write(frame)

        cv2.putText(frame, f'Violence : {preds[0][0]}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, 2)

        frame = cv2.imencode('.jpg', frame)[1]
        frame = frame.tobytes()
        socketio.emit('rtc', frame)
        socketio.sleep(0)

        # k = cv2.waitKey(1)
        # if ord('q') == k:
        #     break


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



