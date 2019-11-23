from queue import Queue
import sqlite3
import re


class Clock:
    def __init__(self):
        self.data_que = Queue()
        self.__task_list = []
        self.clock = 0

# Retrieve data from database
    def retrieve_data(self):
        conn = sqlite3.connect("simulation_data.db")
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY arrival")
        self.__task_list = c.fetchall()
        conn.commit()
        conn.close()

# Putting data into a queue
    def create_task_queue(self):
        for task in self.__task_list:
            self.data_que.put(task)

# Validate the task
    def is_valid_task(self, input):
        self.__valid_count = 0
        self.__upper = re.compile(r'[A-Z]+')
        self.__lower = re.compile(r'[a-z]+')
        self.__number = re.compile(r'[0-9]+')
        self.__special = re.compile(r'[*&#@_-]+')
        if self.__upper.search(input):
            self.__valid_count += 1
        if self.__lower.search(input):
            self.__valid_count += 1
        if self.__number.search(input):
            self.__valid_count += 1
        if self.__special.search(input):
            self.__valid_count += 1
        if self.__valid_count >= 3:
            return True
        return False

# Proceeding tasks
    def proceed_task(self):
        print("** SYSTEM INITIALISED **")
        while not self.data_que.empty():
            self.__current_task = self.data_que.get()
            self.clock = self.__current_task[2]
            print(
                f"** {self.__current_task[2]}: "
                f"Task {self.__current_task[1]} "
                f"with duration {self.__current_task[3]} enters the system.")
            self.__valid_result = self.is_valid_task(self.__current_task[1])
            if self.__valid_result:
                print(f'** Task {self.__current_task[1]} accepted.')
            else:
                print(
                    f'** Task {self.__current_task[1]} '
                    f'unfeasible and discarded.')


class Processor:
    pass


a = Clock()
a.retrieve_data()
a.create_task_queue()
a.proceed_task()
