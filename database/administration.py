import sqlite3


db = sqlite3.connect('server.db')
cr = db.cursor()

key = 'Wizaker'
cr.execute(f'SELECT * FROM users WHERE username = "{key}"')

if cr.fetchone() is not None:
    cr.execute(f'DELETE FROM users WHERE username = "{key}"')
    db.commit()
else:
    print('User isn`t exist!')
