# import
from random import sample, uniform, expovariate
from string import ascii_letters, digits
from math import ceil
import sqlite3


# ID Generator
def id_gen():
    id = ''.join(sample(ascii_letters + digits + "@_#*-&", 6))
    return id


# Arrival Generator
def arrival_gen():
    arrival = uniform(0, 100)
    return arrival


# Duration Generator
def duration_gen():
    duration = ceil(expovariate(1))
    return duration


# Data Generator
def task_gen():
    task_num = 100
    count = 0
    task_list = []
    while count < task_num:
        pid = count + 1
        task_list.append((pid, id_gen(), arrival_gen(), duration_gen()))
        count += 1
    return task_list


# Create databse
conn = sqlite3.connect("simulation_data.db")
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE tasks
(pid INTEGER PRIMARY KEY UNIQUE NOT NULL, id TEXT NOT NULL, arrival INTEGER NOT NULL, duration INTEGER NOT NULL)''')
# Generate data
task = task_gen()
# Insert data
c.executemany("INSERT INTO tasks VALUES (?, ?, ?, ?)", task)
# commit changes and close
conn.commit()
conn.close()
