from flask_restful import Resource
from flask import Response
import tensorflow as tf
from keras.models import load_model
import cv2
import base64
import numpy as np
import time
import uuid
import concurrent.futures

from utils.face_detect import FaceRecognition
from utils.services import create_warning_video


class ViolenceDetection:
    def __init__(self, vc):
        self.model_path = 'utils/violence_model.h5'
        self.model = tf.keras.models.load_model(self.model_path)
        self.frames_list_size = 10
        self.max_v = 6
        self.warning_path = "static/warnings/"
        self.file_name = None
        self.writer = None
        self.isRecording = False
        self.start_time = None
        self.frames_list = []
        self.thread_number = 0
        self.vc = vc
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    def detect_violence(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (128, 128)).astype("float32")
        img = img.reshape(128, 128, 3) / 255
        predictions = self.model.predict(
            np.expand_dims(img, axis=0), verbose=0)
        return predictions[0][0] > 0.5

    def record_violence_video(self, frame, is_violence):
        width = int(self.vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.frames_list.append(is_violence)

        if len(self.frames_list) > self.frames_list_size:
            self.frames_list.pop(0)

        if np.sum(self.frames_list) >= self.max_v and not self.isRecording:
            self.file_name = str(uuid.uuid4())
            self.writer = cv2.VideoWriter(
                f'{self.warning_path}{self.file_name}.mp4', self.fourcc, 20, (width, height))
            self.start_time = time.time()
            self.isRecording = True

        if self.isRecording and time.time() - self.start_time > 10:
            if np.sum(self.frames_list) >= self.max_v:
                self.start_time = time.time()
                self.writer.write(frame)
            else:
                self.writer.release()
                self.isRecording = False
                create_warning_video(self.file_name)
                self.thread_number += 1
                face_thread = concurrent.futures.ThreadPoolExecutor().submit(
                    FaceRecognition, f'{self.file_name}.mp4')
                print(f'thread_number: {self.thread_number}')
        elif self.isRecording:
            self.writer.write(frame)


class VideoStreamer:
    def __init__(self):
        self.vc = None

    def generate(self):
        vc = cv2.VideoCapture("static/john_cena_VS_the_rock_Trim.mp4")
        violence_detection = ViolenceDetection(vc)

        while True:
            if not vc:
                break
            rval, frame = vc.read()

            if not rval or frame is None:
                break

            is_violence = violence_detection.detect_violence(frame)
            violence_detection.record_violence_video(frame, is_violence)

            cv2.putText(frame, f'Violence: {is_violence}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, 2)

            _, encodedImage = cv2.imencode(".jpg", frame)

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    def stream(self):
        return Response(self.generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


class Stream(Resource):
    def get(self):
        video_streamer = VideoStreamer()
        return video_streamer.stream()
