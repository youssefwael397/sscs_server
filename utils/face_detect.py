import face_recognition
import os
import glob
import cv2
import numpy as np
from flask import Response


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
    print('open_RTC')

    while True:
        ret, frame = vc.read()
        if not ret:
            break

        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # detected_faces = face_recognition.face_locations(frame_rgb)

        # for detected_face in detected_faces:
        #     top, right, bottom, left = detected_face
        #     cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
        #     encoding = face_recognition.face_encodings(
        #         frame_rgb, [detected_face])[0]

        #     results = face_recognition.compare_faces(faces, encoding)

        #     name = 'Unknown'
        #     face_distance = face_recognition.face_distance(faces, encoding)
        #     best_match_index = np.argmin(face_distance)

        #     if results[best_match_index]:
        #         name = names[best_match_index]

        #     cv2.putText(frame, name, (left, bottom + 25),
        #                 cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        print(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        socketio.emit('rtc', {"frame": frame})

        # cv2.imshow('video stream', frame)

        k = cv2.waitKey(1)
        if ord('q') == k:
            break

    # close the video capture
    cv2.destroyAllWindows()
    vc.release()


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
