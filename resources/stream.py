from flask_restful import Resource, reqparse, fields
from flask import Response, current_app
from keras.models import load_model
from datetime import datetime
from models.warning import WarningModel
from utils.date_funcs import current_datetime
from utils.services import create_warning_video
import cv2
import base64
import threading
import numpy as np
import time
import uuid



# initialize a lock used to ensure thread-safe
# exchanges of the frames (useful for multiple browsers/tabs
# are viewing tthe stream)
model = load_model('utils/violence_model.h5')
# Define the codec to use for the video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
warning_path = "static/warnings/"
file_name = None
lock = threading.Lock()
vc = None
out = None
frames_list = []
isRecording = False
start_time = None
frames_list_size = 5
max_v = 3
v_count = 0
writer = None



def violence_detection(frame):
    global model

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (128, 128)).astype("float32")
    img = img.reshape(128, 128, 3) / 255
    predictions = model.predict(np.expand_dims(img, axis=0), verbose=0)
    preds = predictions > 0.5
    return preds[0][0]

def record_violence_video(frame, is_violence):
    global warning_path, file_name, isRecording, frames_list, start_time, v_count, writer, max_v, vc

    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Append the current frame to the frames_list
    frames_list.append(is_violence)

    # If there are more than frames_list_size violent frames in the list, remove the oldest frames
    if len(frames_list) > frames_list_size:
        frames_list.pop(0)

    if np.sum(frames_list) >= max_v and not isRecording:
        # print('not recording')
        file_name = uuid.uuid4()

        # Save warning video file to /static/warning
        # print('before start recording')
        writer = cv2.VideoWriter(f'{warning_path}{file_name}.mp4', fourcc, 10, (width, height))
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
            v_count = 0
            isRecording = False
            # save violence video in db 
            create_warning_video(file_name)

    # If isRecording is True and the recording time has not exceeded 10 seconds, write the current frame to the video
    elif isRecording:
        # print('recording')
        writer.write(frame)


def generate():
    # grab global references to the lock variable
    global lock
    global vc
    global writer

    print('vc', vc)
    vc = cv2.VideoCapture('static/full_v.mp4')

    # check camera is open
    if vc.isOpened():
        rval, frame = vc.read()
        print('vc is opened')
    else:
        print('vc is not defined')
        rval = False

    while rval:
        # wait until the lock is acquired
        with lock:
            # read next frame
            rval, frame = vc.read()

            # if blank frame
            if frame is None:
                continue

            # call a function that violence detection 
            is_violence = violence_detection(frame)
            record_violence_video(frame, is_violence)
            # then call a function that face recognition 

            # add text to the frame 
            cv2.putText(frame, f'Violence : {is_violence}', (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, 2)
            
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", frame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
    # release the camera
    if writer:
        writer.release()
    vc.release()


class Stream(Resource):
    def get(self):
        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
