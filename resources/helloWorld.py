from flask_restful import Resource


class HelloWorld(Resource):
    def get(self):
        return {
            "status": "ok",
            "message": "Hello World!"
        }, 200
