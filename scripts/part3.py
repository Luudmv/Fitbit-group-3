import sqlite3

con = sqlite3.connect("fitbit_database.db")
cur = con.cursor()

# res = cur.execute("SELECT name FROM sqlite_master")
# print(res.fetchall())

# for row in cur.execute("SELECT * FROM hourly_steps"):
#     print(row)

cur.execute("SELECT * FROM hourly_steps")
column_names = [description[0] for description in cur.description]

print(column_names)

con.close()
