from factory import create_app
from flask_restful import Api
from flask import send_file
# from utils.smtp_service import send_violence_notification
from utils.notification import send_violence_notification

# import models to create at runtime
from models.user import UserModel
from models.warning import WarningModel
from models.user_warning import UserWarningModel

# import api routes from resources
from resources.user import UserRegister, Users, User
from resources.warning import Warnings, Warning , WarningsVideo
from resources.helloWorld import HelloWorld
from resources.user_warning import UserWarningByUser,UsersByWarningId,WarningByUserId , UserWarnings, UserWarning, WarningExtractFaces
# from resources.stream import Stream, StopStream, StartStream
from resources.new_stream import Stream



app = create_app()
api = Api(app)

# api routes
api.add_resource(HelloWorld, '/')
# Users
api.add_resource(UserRegister, '/api/register')
api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:user_id>')
# warnings
api.add_resource(Warnings, '/api/warnings')

api.add_resource(WarningsVideo, '/api/warnings/video/<filename>')
# api.add_resource(CreateWarning, '/api/warnings/create')
api.add_resource(Warning, '/api/warnings/<int:warning_id>')
# user_warnings
api.add_resource(UserWarnings, '/api/user_warnings')
# get the details of warnings associated with a specific user
api.add_resource(WarningByUserId , '/api/user_warnings/warnings/<int:user_id>')
# get users details of a warning by id 
api.add_resource(UsersByWarningId , '/api/user_warnings/users/<int:warning_id>')

api.add_resource(WarningExtractFaces, '/api/user_warnings/extract/<int:warning_id>')
api.add_resource(UserWarning, '/api/user_warnings/<int:user_warning_id>')
# api.add_resource(UserWarningByUser, '/api/user_warnings/<int:user_id>')   
# video_stream = VideoStream()
api.add_resource(Stream, '/stream')
# api.add_resource(StartStream, '/stream/start')
# api.add_resource(StopStream, '/stream/stop')


# send_violence_notification()

@app.route('/video/<path:filename>')
def get_video(filename):
    path = f'{filename}'
    print(filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8000
    debug = True
    options = None
    app.run(host, port, debug, options, threaded=True)
