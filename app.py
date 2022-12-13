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
from utils.face_detect import get_faces_paths_and_names, get_faces, count_faces_from_video
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

# socketio events
@socketio.on('connect')
def test_connect():
    print('Pyramids')
    socketio.emit('connect', {'connected': True, 'name': 'Pyramids'})


@socketio.on('json')
def handle_my_custom_event(json):
    print('received json: ' + str(json))




# registered_faces_path = 'static/users/'
# names, faces_paths = get_faces_paths_and_names(registered_faces_path)
# faces = get_faces(faces_paths)

# names, count = count_faces_from_video('static/users/elharam/elharam.webm', faces, names)
# print("names: ", names)
# print("count: ", count)


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(host='0.0.0.0', debug=True)
