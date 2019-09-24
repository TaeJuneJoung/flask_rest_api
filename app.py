from flask import Flask, escape, request
from flask_restplus import reqparse, abort, Api, Resource
from flask_cors import CORS
import database

app = Flask(__name__)
CORS(app)
api = Api(app)

name_space = api.namespace('api',description='Main APIs')

@name_space.route('/todos')
class Todos(Resource):
    def get(self):
        return database.get_todos()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('work', type=str, required=True)
        args = parser.parse_args()
        database.post_todo(args)
        return args

@name_space.route('/todo/<int:id>')
class Todo(Resource):
    def get(self, id):
        try:
            data = database.get_todo(id)
        except TypeError:
            data = abort(404, message=f"Todo id:{id} doesn't exist")
        return data
    
    def put(self, id):
        try:
            database.get_todo(id)
            parser = reqparse.RequestParser()
            parser.add_argument('work', type=str, required=True)
            args = parser.parse_args()
            database.put_todo(id, args['work'])
        except TypeError:
            args = abort(404, message=f"Todo id:{id} doesn't exist")
        return args

    def delete(self, id):
        try:
            database.get_todo(id)
            database.delete_todo(id)
            data = {"message": "Delete"}
        except TypeError:
            data = abort(404, message=f"Todo id:{id} doesn't exist")
        return data

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

if __name__ == '__main__':
    app.run(debug=True)