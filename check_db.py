import sqlite3

con = sqlite3.connect('db.sqlite3')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables found:")
for t in tables:
    print(t[0])
con.close()
