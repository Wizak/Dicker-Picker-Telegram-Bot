import sqlite3

db = sqlite3.connect('server.db')
cr = db.cursor()

cr.execute('''CREATE TABLE users(
    chat_id,
    user_id TEXT,
    username TEXT,
    frist_name TEXT,
    last_name TEXT,
    dick INTEGER,
    pick_time TEXT
)''')

db.commit()
db.close()
