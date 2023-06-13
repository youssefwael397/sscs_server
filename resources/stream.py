from flask_restful import Resource
from flask import Response
import tensorflow as tf
from keras.models import load_model
import cv2
import base64
import threading
import numpy as np
import time
import uuid
import concurrent.futures
from functools import partial
import multiprocessing


from utils.faceRecThread import FaceRecognition
from utils.services import create_warning_video

model_path = 'utils/violence_model.h5'
model = tf.keras.models.load_model(model_path)
face_recognition_done = multiprocessing.Event()
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
warning_path = "static/warnings/"
file_name = None
lock = threading.Lock()
writer_lock = threading.Lock()
vc = None
frames_list = []
isRecording = False
start_time = None
frames_list_size = 10
max_v = 8
writer = None
thread_number = 0
# Initialize last_pts variable
last_pts = -1


def violence_detection(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (128, 128)).astype("float32")
    img = img.reshape(128, 128, 3) / 255
    predictions = model.predict(np.expand_dims(img, axis=0), verbose=0)
    # return True
    return predictions[0][0] > 0.5


def record_violence_video(frame, is_violence):
    global warning_path, file_name, isRecording, frames_list, start_time, writer, max_v, vc, thread_number, face_recognition_done

    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Append the current frame to the frames_list
    frames_list.append(is_violence)

    # If there are more than frames_list_size violent frames in the list, remove the oldest frames
    if len(frames_list) > frames_list_size:
        frames_list.pop(0)

    if np.sum(frames_list) >= max_v and not isRecording:
        file_name = str(uuid.uuid4())

        # Save warning video file to /static/warning
        writer = cv2.VideoWriter(
            f'{warning_path}{file_name}.mp4', fourcc, 20, (width, height))
        start_time = time.time()
        isRecording = True

    # If isRecording is True and the recording time has exceeded 10 seconds
    if isRecording and time.time() - start_time > 10:
        # If there are at least two violent frames in the list, write the current frame to the video
        if np.sum(frames_list) >= max_v:
            start_time = time.time()
            writer.write(frame)
        # Otherwise, release the writer and reset the variables
        else:
            writer.release()
            isRecording = False
            # save violence video in db
            create_warning_video(file_name)
            # create a new thread to perform face recognition
            thread_number += 1
            face_process = multiprocessing.Process(
                target=FaceRecognition, args=(f'{file_name}.mp4',))
            face_process.start()
            # face_thread = threading.Thread(
            #     target=FaceRecognition, args=(f'{file_name}.mp4',))
            # face_thread.start()
            print(f'thread_number: {thread_number}')

    # If isRecording is True and the recording time has not exceeded 10 seconds, write the current frame to the video
    elif isRecording:
        writer.write(frame)


def performViolenceDetection(frame):
    global vc, writer, warning_path, file_name, isRecording, frames_list, start_time, max_v, thread_number, writer_lock

    is_violence = violence_detection(frame)
    # print("is_violence: ", is_violence)

    # Append the current frame to the frames_list
    with lock:
        frames_list.append(is_violence)

    # If there are more than frames_list_size violent frames in the list, remove the oldest frames
    if len(frames_list) > frames_list_size:
        with lock:
            frames_list.pop(0)

    

def performVideoWriting(frame):
    global vc, writer, warning_path, file_name, isRecording, frames_list, start_time, max_v, thread_number, lock

    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if np.sum(frames_list) >= max_v and not isRecording and writer is None: 
        file_name = str(uuid.uuid4())

        # Save warning video file to /static/warning
        writer = cv2.VideoWriter(
            f'{warning_path}{file_name}.mp4', fourcc, 20, (width, height))

        print("create new video writer")

        start_time = time.time()
        isRecording = True


    # If isRecording is True and the recording time has exceeded 10 seconds
    if isRecording and time.time() - start_time > 10:
        # If there are at least two violent frames in the list, write the current frame to the video
        if np.sum(frames_list) >= max_v:
            start_time = time.time()
            print('before writing after 10 seconds')
            try:
                writer.write(frame)
                # print('writing')
            except Exception as e:
                print('error writing frame: ', e)
            print("writing frame to " + str(start_time))
        # Otherwise, release the writer and reset the variables
        else:
            writer.release()
            writer = None
            print("releasing writer")
            isRecording = False
            # Save violence video in the database
            create_warning_video(file_name)
            # Create a new thread to perform face recognition
            face_process = multiprocessing.Process(target=FaceRecognition, args=(f'{file_name}.mp4',))
            face_process.start()
            # with lock:
            #     thread_number += 1
            #     # Create a new process to perform face recognition
            print("after calling face recognition")

    # If isRecording is True and the recording time has not exceeded 10 seconds, write the current frame to the video
    elif isRecording and writer is not None:
        try:
            writer.write(frame)
            # print('writing')
        except Exception as e:
            print('error writing frame: ', e)


def generate():
    global lock, vc, writer

    print("Generating")
    # "static/john_cena_VS_the_rock_Trim.mp4"
    vc = cv2.VideoCapture("static/new_violence.mp4")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            if not vc:
                print("No video capture found")
                break
            rval, frame = vc.read()

            if not rval or frame is None:
                print("No frame or rval found")
                break

            performVideoWriting(frame.copy())
            # Execute the performViolenceDetection function asynchronously in a separate thread
            executor.submit(performViolenceDetection, frame.copy())

            _, encodedImage = cv2.imencode(".jpg", frame)

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        if writer is not None:
            writer.release()
            writer = None

        if vc is not None:
            vc.release()
            vc = None
        
        print("Streaming stopped")


class Stream(Resource):
    def get(self):
        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


class StartStream(Resource):
    def get(self):
        global vc
        if vc:
            return {"message": "Stream is already started."}, 404
        # static/john_cena_VS_the_rock_Trim.mp4
        vc = cv2.VideoCapture(0)
        return {"message": "Started video streaming."}


class StopStream(Resource):
    def get(self):
        global vc
        if vc:
            vc.release()
            vc = None
            return {"message": "Stream is being closed successfully."}, 200
        return {"message": "Stream is already closed."}, 404
