from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from config import mysql_uri
from db import db
# import models to create at runtime
from models.user import UserModel
from models.warning import WarningModel
from models.user_warning import UserWarningModel
# import api routes from resources
from resources.user import UserRegister, Users, User
from resources.warning import Warnings, Warning, CreateWarning
from resources.helloWorld import HelloWorld
from resources.user_warning import UserWarningByUser, UserWarnings, UserWarning
# import helpers
from utils.file_handler import extract_and_save_faces
from utils.face_detect import open_RTC_violence
from utils.date_funcs import current_datetime
# import flask_socketio to serve the project
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
api.add_resource(UserRegister, '/api/register')
api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:user_id>')
# warnings
api.add_resource(Warnings, '/api/warnings')
api.add_resource(CreateWarning, '/api/warnings/create')
api.add_resource(Warning, '/api/warnings/<int:warning_id>')
# user_warnings
api.add_resource(UserWarnings, '/api/user_warnings')
api.add_resource(UserWarning, '/api/user_warnings/<int:user_warning_id>')
api.add_resource(UserWarningByUser, '/api/user_warnings/<int:user_id>')

# registered_faces_path = 'static/users/'
# names, faces_paths = get_faces_paths_and_names(registered_faces_path)
# faces = get_faces(faces_paths)

# socketio events
@socketio.on('connect')
def test_connect():
    print('Pyramids')
    print(current_datetime())
    open_RTC_violence(socketio)
    socketio.emit('connect', {'connected': True, 'name': 'Pyramids'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(host='0.0.0.0', debug=True)
