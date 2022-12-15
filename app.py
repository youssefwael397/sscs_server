from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from config import mysql_uri
from db import db
# import models to create at runtime
from models.user import UserModel
from resources.user import UserRegister, Users, User, ChangePassword, CreateStaticUser
from resources.helloWorld import HelloWorld
from utils.file_handler import extract_and_save_faces
from utils.face_detect import get_faces_paths_and_names, get_faces, open_face_detect_cam, open_RTC, close_stream
from flask_socketio import SocketIO, emit, send

app = Flask(__name__, static_url_path='/static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

socketio = SocketIO(app, cors_allowed_origins='*')


app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.before_first_request
def create_tables():
    db.init_app(app)
    db.create_all()


# api routes
api.add_resource(HelloWorld, '/')  # base api url http://localhost:5000/
# Users
# api.add_resource(CreateStaticUser, '/api/static/user/create') # for test
api.add_resource(UserRegister, '/api/register')
api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:user_id>')

registered_faces_path = 'static/users/'
names, faces_paths = get_faces_paths_and_names(registered_faces_path)
faces = get_faces(faces_paths)

# socketio events


@socketio.on('connect')
def test_connect():
    print('Pyramids')
    open_RTC(faces, names, socketio)
    # socketio.emit('connect', {'connected': True, 'name': 'Pyramids'})


@socketio.on('close_stream')
def handle_find_face():
    close_stream()
    # socketio.emit('response', {'connected': True, 'frame': json})


@socketio.on('face_recognition')
def handle_find_face(json):
    open_face_detect_cam()
    print(json)
    socketio.emit('response', {'connected': True, 'frame': json})


# registered_faces_path = 'static/users/'
# names, faces_paths = get_faces_paths_and_names(registered_faces_path)
# faces = get_faces(faces_paths)

# names, count = count_faces_from_video('static/users/elharam/elharam.webm', faces, names)
# print("names: ", names)
# print("count: ", count)


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(host='0.0.0.0', debug=True)
