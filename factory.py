from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from config import mysql_uri
from db import db


# import helpers
from utils.file_handler import extract_and_save_faces
from utils.face_detect import open_RTC_violence
from utils.date_funcs import current_datetime

def create_app():
    app = Flask(__name__, static_url_path='/static')
    cors = CORS(app, resources={r"/api/": {"origins": ""}})

    app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app
