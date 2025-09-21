import sqlite3 as sql

conn = sql.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS tennisreservations (name TEXT, school TEXT, court TEXT, times TEXT, available TEXT)')
cur = conn.cursor()
cur.execute("INSERT INTO tennisreservations (name,school,court,times, available) VALUES (?,?,?,?,?)",('', 'DVHS', 'Court 1', '7-9AM', 'Yes'))       
conn.close()
