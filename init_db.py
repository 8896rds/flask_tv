import sqlite3

connection = sqlite3.connect('tv_database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO tv (channel_name, link,channel_group) VALUES (?, ?, ?)",
            ('test1', 'www.test.com','test')
            )

connection.commit()
connection.close()