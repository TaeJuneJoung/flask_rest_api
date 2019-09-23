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
        SELECT * FROM todos;
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