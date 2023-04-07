from flask_restful import Resource, reqparse, fields
from flask import Response
from keras.models import load_model
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
warning_path = "static/warnings/"
lock = threading.Lock()
vc = None
out = None
frames_list = []
isRecording = False
start_time = None
max_v = 5
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
    global warning_path, isRecording, frames_list, start_time, v_count, writer, max_v, vc

    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Append the current frame to the frames_list
    frames_list.append(is_violence)

    # If there are more than max_v violent frames in the list, remove the oldest frames
    if len(frames_list) > max_v:
        frames_list.pop(0)

    # If the current frame is violent and the v_count is less than max_v, increment v_count
    if is_violence and v_count < max_v:
        v_count += 1

    # If the v_count has reached max_v and isRecording is False, start recording
    if v_count == max_v and not isRecording:
        # print('not recording')
        file_name = uuid.uuid4()

        # Save warning video file to /static/warning
        # print('before start recording')
        writer = cv2.VideoWriter(f'{warning_path}{file_name}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 10, (width, height))
        start_time = time.time()
        isRecording = True

    # If isRecording is True and the recording time has exceeded 10 seconds
    if isRecording and time.time() - start_time > 10:
        # print(frames_list)

        # If there are at least two violent frames in the list, write the current frame to the video
        if np.sum(frames_list) > 1:
            start_time = time.time()
            writer.write(frame)

        # Otherwise, release the writer and reset the variables
        else:
            writer.release()
            v_count = 0
            isRecording = False

    # If isRecording is True and the recording time has not exceeded 10 seconds, write the current frame to the video
    elif isRecording:
        # print('recording')
        writer.write(frame)


def generate():
    # grab global references to the lock variable
    global lock
    global vc
    global out

    print('vc', vc)
    vc = cv2.VideoCapture(0)

    # check camera is open
    if vc.isOpened():
        print('vc is opened')
        rval, frame = vc.read()
    else:
        print('vc is not defined')
        rval = False

    while rval:
        # wait until the lock is acquired
        with lock:
            # read next frame
            rval, frame = vc.read()
            # print('out: ', out)


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
    out.release()
    vc.release()


class Stream(Resource):
    def get(self):
        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
