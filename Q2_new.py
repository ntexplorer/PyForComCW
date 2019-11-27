from queue import Queue
import sqlite3
import re


# Retrieve task from database, store and move tasks between queues
class TaskStorage():
    def __init__(self):
        self.task_list = []
        self.enter_queue = Queue()
        self.onhold_queue = Queue()

    def get_data(self, database="simulation_data.db"):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY arrival")
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
    def __init__(self, id, status=True):
        self.id = id
        self.status = status

    def check_status(self):
        return self.status

    # Situation 1
    def proceed_task_1(self, task):
        print(f"** {task[2]} : Task {task[1]} assigned to processor {self.id}")
        self.status = False

    def task_done(self, task):
        print(f"**")
        self.status = True


# Set timer, update time
class Clock():
    def __init__(self):
        self.arrival_list = []
        self.comlete_list = []

    def get_arrval_list(self, task_list):
        for task in task_list:
            self.arrival_list.append(task[2])
        self.arrival_list.sort(reverse=True)
        return self.arrival_list


# Control the whole procedure
class SchedulerService():
    def __init__(self):
        self.processor1 = Processor(1)
        self.processor2 = Processor(2)
        self.processor3 = Processor(3)
        self.clock = Clock()
        self.processor_list = [self.processor1,
                               self.processor2, self.processor3]
        self.task = TaskStorage()
        self.task_list = self.task.get_data()
        self.enter_queue = self.task.enter_queue
        self.onhold_queue = self.task.onhold_queue
        self.validator = Validator()

    def p_task_init(self):
        print("** SYSTEM INITIALISED **")

    def p_enter_system(self, task):
        print(
            f"** {task[2]}: "
            f"Task {task[1]} "
            f"with duration {task[3]} enters the system.")

    def p_task_accepted(self, task):
        print(f'** Task {task[1]} accepted.')

    def p_task_discard(self, task):
        print(
            f'** Task {task[1]} '
            + 'unfeasible and discarded.')

    def proceed(self):
        self.p_task_init()
        self.task.put_enter_queue(self.task_list)
        self.arrival_list = self.clock.get_arrval_list(self.task_list)
        while not self.enter_queue.empty():
            # Situation 1: When the on hold queue is empty.
            if self.onhold_queue.empty():
                self.current_task = self.enter_queue.get()
                self.p_enter_system(self.current_task)
                self.__valid_result = self.validator.is_valid_task(
                    self.current_task[1])
                if self.__valid_result:
                    self.p_task_accepted(self.current_task)
                    # Stuation 1-1: When at least 1 processor is available.
                    if self.processor1.check_status() or self.processor2.check_status() or self.processor3.check_status():
                        if self.processor1.check_status():
                            self.processor1.proceed_task_1(self.current_task)
                        elif self.processor2.check_status():
                            self.processor2.proceed_task_1(self.current_task)
                        else:
                            self.processor3.proceed_task_1(self.current_task)
                    # Stuation 1-2: When no processor is available.
                    else:
                        self.task.put_onhold_queue(self.current_task)
                else:
                    self.p_task_discard(self.current_task)


a = SchedulerService()
a.proceed()
