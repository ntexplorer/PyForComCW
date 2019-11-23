import sqlite3

# conn = sqlite3.connect("simulation_data.db")
# c = conn.cursor()
# c.execute("SELECT * FROM tasks")
# count = 1
# for result in c:
#     print(result)
#     count += 1
# conn.commit()
# conn.close()


# import math
# import random
#
# a = math.ceil(0.1)
# b = math.ceil(1.2)
# i = 1
# d = []
# while i < 20:
#     c = random.uniform(0, 5)
#     d.append(c)
#     i += 1
#
# print(a)
# print(b)
# print(d)

def retrieve_data():
    conn = sqlite3.connect("simulation_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks ORDER BY arrival")
    print(c.fetchall())
    conn.commit()
    conn.close()


retrieve_data()
