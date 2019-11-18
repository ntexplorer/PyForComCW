import sqlite3

conn = sqlite3.connect("simulation_data.db")
c = conn.cursor()
c.execute("SELECT * FROM tasks")
count = 1
for result in c:
    print(result)
    print(str(count))
    count += 1

conn.close()
