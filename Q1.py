# import
import random
import string
import math
import sqlite3


# ID Generator
def id_gen():
    id = ''.join(random.sample(string.ascii_letters +
                               string.digits + "@_#*-&", 6))
    return id


# Arrival Generator
def arri_gen():
    arrival = random.randint(0, 100)
    return arrival


# Duration Generator
def dura_gen():
    duration = math.ceil(random.expovariate(1))
    return duration


# Generate data
def task_gen():
    task_num = 100
    count = 0
    task = []
    while count < task_num:
        task.append((id_gen(), arri_gen(), dura_gen()))
        count += 1
    return task


# Create databse
conn = sqlite3.connect("simulation_data.db")
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE tasks
(id TEXT PRIMARY KEY UNIQUE NOT NULL, arrival INTEGER NOT NULL, duration INTEGER NOT NULL)''')
# Insert data
task = task_gen()
c.executemany("INSERT INTO tasks VALUES (?, ?, ?)", task)
# commit changes and close
conn.commit()
conn.close()
