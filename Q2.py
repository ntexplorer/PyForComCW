from queue import Queue
from queue import LifoQueue
import sqlite3
import re


# Retrieve task from database, store and move tasks between queues
class TaskStorage():
    def __init__(self):
        self.task_list = []
        self.enter_queue = LifoQueue()
        self.onhold_queue = Queue()

    def get_data(self, database="simulation_data.db"):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY arrival DESC")
        self.task_list = c.fetchall()
        conn.commit()
        conn.close()
        return self.task_list

    def put_enter_queue(self, task_list):
        for task in task_list:
            self.enter_queue.put(task)

    def put_onhold_queue(self, task):
        print(f"** Task {task[1]} on hold.")
        self.onhold_queue.put(task)


# Task validator
class Validator():
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


# Processor provide the method to deal with tasks
class Processor():
    def __init__(self, id,):
        self.id = id
        self.status = True
        self.task = ()
        self.end_time = 0

    def check_status(self):
        return self.status

    def proceed_task(self, time, task):
        print(f"** {time} : Task {task[1]} assigned to processor {self.id}")
        self.status = False
        self.task = task
        self.end_time = time + task[3]

    def task_done(self):
        print(f"** {self.end_time} : Task {self.task[1]} completed.")
        self.status = True
        self.task = ()


# Update time
class Clock():
    def __init__(self):
        self.time = 0
        self.next_arrival_time = 0
        self.end_time_ls = []

    def get_next_arrival(self, task):
        self.next_arrival_time = task[2]

    def get_next_end(self, time):
        self.end_time_ls.append(time)

    def del_next_end(self):
        self.end_time_ls.remove(self.time)


# Control the whole procedure
class SchedulerService():
    def __init__(self):
        self.trigger = True
        self.processor1 = Processor(1)
        self.processor2 = Processor(2)
        self.processor3 = Processor(3)
        self.clock = Clock()
        self.task = TaskStorage()
        self.task_list = self.task.get_data()
        self.enter_queue = self.task.enter_queue
        self.onhold_queue = self.task.onhold_queue
        self.validator = Validator()

    def p_sys_init(self):
        print("** SYSTEM INITIALISED **")

    def p_enter_system(self, task):
        print(
            f"** {task[2]} : "
            f"Task {task[1]} "
            f"with duration {task[3]} enters the system.")

    def get_valid_result(self, task):
        self.__valid_result = self.validator.is_valid_task(task[1])
        return self.__valid_result

    def find_processor(self, end_time):
        if self.processor1.end_time == end_time:
            return self.processor1
        elif self.processor2.end_time == end_time:
            return self.processor2
        elif self.processor3.end_time == end_time:
            return self.processor3

    def p_task_accepted(self, task):
        print(f'** Task {task[1]} accepted.')

    def p_task_discard(self, task):
        print(
            f'** Task {task[1]} '
            + 'unfeasible and discarded.')

    def p_sys_completed(self, time):
        print(f"** {time} : SIMULATION COMPLETED. **")

    def check(self):
        print(self.processor1.task,
              self.processor2.task, self.processor3.task)
        print(self.clock.end_time_ls)
        print(self.clock.time)

    def proceed(self):
        self.p_sys_init()
        self.task.put_enter_queue(self.task_list)
        # Check if tasks have all entered the system
        while not self.enter_queue.empty():
            # Get one task from enter_queue
            self.current_task = self.enter_queue.get()
            self.clock.get_next_arrival(self.current_task)
            if self.clock.end_time_ls:
                self.check()
                if min(self.clock.end_time_ls) <= self.clock.next_arrival_time:
                    self.enter_queue.put(self.current_task)
                    self.clock.time = min(self.clock.end_time_ls)
                    self.processor_found = self.find_processor(
                        self.clock.time)
                    self.processor_found.task_done()
                    self.clock.del_next_end()
                    if not self.onhold_queue.empty():
                        self.first_onhold = self.onhold_queue.get()
                        self.processor_found.proceed_task(
                            self.clock.time, self.first_onhold)
                        self.clock.get_next_end(self.processor_found.end_time)
                else:
                    self.p_enter_system(self.current_task)
                    if self.get_valid_result(self.current_task):
                        self.p_task_accepted(self.current_task)
                        if self.processor1.check_status():
                            self.processor1.proceed_task(
                                self.current_task[2], self.current_task)
                            self.clock.get_next_end(self.processor1.end_time)
                        elif self.processor2.check_status():
                            self.processor2.proceed_task(
                                self.current_task[2], self.current_task)
                            self.clock.get_next_end(self.processor2.end_time)
                        elif self.processor3.check_status():
                            self.processor3.proceed_task(
                                self.current_task[2], self.current_task)
                            self.clock.get_next_end(self.processor3.end_time)
                        else:
                            self.task.put_onhold_queue(self.current_task)
                    else:
                        self.p_task_discard(self.current_task)
            else:
                self.check()
                self.p_enter_system(self.current_task)
                if self.get_valid_result(self.current_task):
                    self.p_task_accepted(self.current_task)
                    self.processor1.proceed_task(
                        self.current_task[2], self.current_task)
                    self.clock.get_next_end(self.processor1.end_time)
                else:
                    self.p_task_discard(self.current_task)
        print("***************")
        while not len(self.clock.end_time_ls) == 0:
            self.check()
            self.clock.time = min(self.clock.end_time_ls)
            self.processor_found = self.find_processor(
                self.clock.time)
            self.processor_found.task_done()
            self.clock.del_next_end()
            if not self.onhold_queue.empty():
                self.first_onhold = self.onhold_queue.get()
                self.processor_found.proceed_task(
                    self.clock.time, self.first_onhold)
                self.clock.get_next_end(self.processor_found.end_time)
        self.p_sys_completed(self.clock.time)


a = SchedulerService()
a.proceed()
