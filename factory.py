from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from config import mysql_uri
from db import db

def create_app():
    app = Flask(__name__, static_url_path='/static')
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['VIDEO_FOLDER'] = 'static/warnings'
    
    @app.before_first_request
    def create_tables():
        db.create_all()
    db.init_app(app)

    return app
