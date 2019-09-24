# Flask RESTFUL API

​	Flask RESTFUl API를 만드는 방법에 대해서 학습해보고자 한다.



## Install

```bash
pip install flask
pip install flask_restful
pip install flask-cors
```





## Flask Settings

​	먼저, Flask를 만들어보자.

[Flask Docs](https://palletsprojects.com/p/flask/)를 보고 따라하면 된다. 먼저 아래의 소스를 `app.py`를 생성하여 넣어보자. 작성 후에 `python app.py`를 실행해보면 Flask 서버를 실행할 수 있다.

```python
from flask import Flask, escape, request

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

if __name__ == '__main__':
    app.run(debug=True)
```



## Connect Database

​	값을 가져오기 위해서 Database와 연동하자. DB는 Flask와 연결되어 있는 sqlite3를 사용하도록 하겠다. 다른 DB를 사용하고 싶으면 갈아 끼우고 그에 맞는 설정만 하면 그만이다.

```python
import os
import sqlite3

# database 폴더가 없다면 생성
if not os.path.isdir('database'):
    os.mkdir('database')

conn = None
cur = None

def conn():
    global conn, cur
    conn = sqlite3.connect('database/database.db')
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS todos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work TEXT,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

def close():
    global conn, cur
    conn.commit()
    cur.close()
    conn.close()
    cur = None
    conn = None


def get_todos():
    global conn, cur
    conn()
    cur.execute('''
        SEELCT * FROM todos;
    ''')
    data = cur.fetchall()
    close()
    return data

def get_todo(id):
    global conn, cur
    conn()
    cur.execute(f'''
        SELECT * FROM todos
        WHERE id = {id};
    ''')
    data = cur.fetchone()
    close()
    return data

def post_todo(work):
    global conn, cur
    conn()
    cur.execute(f"""
        INSERT INTO todos (work)
        VALUES ('{work}');
    """)
    close()

def put_todo(id, work):
    global conn, cur
    conn()
    cur.execute(f"""
        UPDATE todos
        SET work = '{work}'
        WHERE id = {id};
    """)
    close()

def delete_todo(id):
    global conn, cur
    conn()
    cur.execute(f'''
        DELETE FROM todos
        WHERE id = {id};
    ''')
    close()
```

​	ORM형식으로 짠 것이 아니라 그런지, 발생한 이슈는 `Text`타입일 때 Insert나 Update SQL Query에서 `'`싱글 쿼터나 더블 쿼터로 감싸주지 않아서 타입 오류가 발생하였다. 이에 대한 대응책도 하나 마련해야한다. 싱글 쿼터로 감싸주었는데 값에 싱글 쿼터가 있다면 SQL Injection이 발생하고 말 것이다. 여기에는 작성하지 않았지만, 이를 해결하기 위해서 python의 `replace문`을 사용할 수 있다.



## BASIC RESTFUL API

​	에러처리 없는 기본적인 REST API는 아래와 같다.

```python
from flask import Flask, escape, request
from flask_restful import reqparse, abort, Api, Resource
import database

app = Flask(__name__)

api = Api(app)

class Todos(Resource):
    def get(self):
        return database.get_todos()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('work', type=str, required=True)
        args = parser.parse_args()
        database.post_todo(args)
        return args

class Todo(Resource):
    def get(self, id):
        return database.get_todo(id)
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('work', type=str, required=True)
        args = parser.parse_args()
        database.put_todo(id, args['work'])
        return args

    def delete(self, id):
        database.delete_todo(id)

api.add_resource(Todos, '/todos')
api.add_resource(Todo, '/todo/<int:id>')

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

if __name__ == '__main__':
    app.run(debug=True)
```

​	테스트 해보던 중에 한가지 문제가 발생하였다. get으로 가져온 다음에 F5를 누르면 해당 값이 `None`이 되면서 **TypeError**을 발생하는 것이었다. 데이터베이스 구조에서 **close**를 해주기에 생기는 문제였는데,  이는 sqlite3에서 발생하였다.  sqlite3는 동시성이 필요한 작업에서는 사용하지 않는 것이 좋다.



​	DB를 고려하지 않는다고 하였을 때도 새로운 문제가 발생한다. 다른 주소에서 접근을 할 수가 없는 문제있다. 이를 해결하기 위해서 CORS를 설정해주어야한다.

### CORS

**Cross-Origin Resource Sharing**

: 시스템 수준에서 타 도메인 간 자원 호출을 승인하거나 차단하는 것을 결정하는 것





## 완성 RESTFUL API

```python
from flask import Flask, escape, request
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import database

app = Flask(__name__)
CORS(app)
api = Api(app)

class Todos(Resource):
    def get(self):
        return database.get_todos()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('work', type=str, required=True)
        args = parser.parse_args()
        database.post_todo(args)
        return args

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

api.add_resource(Todos, '/todos')
api.add_resource(Todo, '/todo/<int:id>')

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

if __name__ == '__main__':
    app.run(debug=True)
```



## Swagger

```bash
pip install flask_restplus
```

```python
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
```

`restplus`에 있는 `namespace()`를 이용하여 **swagger**와 연결하여 API 문서를 만들수 있다.



### 참고 자료

[SQLite 장단점](http://egloos.zum.com/sweeper/v/3052951)

[Flask-Restful Docs](https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html)