from queue import Queue
from queue import LifoQueue
import sqlite3
import re


# Retrieve task from database, store and move tasks between queues
class TaskStorage():
    def __init__(self):
        self.task_list = []
        '''
        Creating two queues, one for task entering the system(from database),
        the other one for task onhold
        '''
        self.enter_queue = LifoQueue()
        # Using a LifoQueue because operation involves putting back task to the queue
        self.onhold_queue = Queue()

    def get_data(self, database="simulation_data.db"):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        # retrieve tasks ordered by arrival time, reversed
        c.execute("SELECT * FROM tasks ORDER BY arrival DESC")
        # fetch all tasks and store them in a list
        self.task_list = c.fetchall()
        conn.commit()
        conn.close()
        return self.task_list

    def put_enter_queue(self, task_list):
        # use for loop to put all the tasks into the enter_queue
        for task in task_list:
            self.enter_queue.put(task)

    def put_onhold_queue(self, task):
        print(f"** Task {task[1]} on hold.")
        self.onhold_queue.put(task)


# Task validator
class Validator():
    def is_valid_task(self, input):
        self.__valid_count = 0
        # make a regular expression for each condition
        self.__upper = re.compile(r'[A-Z]+')
        self.__lower = re.compile(r'[a-z]+')
        self.__number = re.compile(r'[0-9]+')
        self.__special = re.compile(r'[*&#@_-]+')
        # add 1 to valid count if meets one of the requirements
        if self.__upper.search(input):
            self.__valid_count += 1
        if self.__lower.search(input):
            self.__valid_count += 1
        if self.__number.search(input):
            self.__valid_count += 1
        if self.__special.search(input):
            self.__valid_count += 1
        # valid count>=3 means it has more than 3 kind of elements(valid)
        if self.__valid_count >= 3:
            return True
        return False


# Processor provide the method to deal with tasks
class Processor():
    def __init__(self, id,):
        self.id = id
        self.status = True
        # Attribute task contains the task entering the processor
        self.task = ()
        self.end_time = 0

    def check_status(self):
        return self.status

    # this function takes two args, the actual time for task entering the processor
    def proceed_task(self, time, task):
        print(f"** {time} : Task {task[1]} assigned to processor {self.id}")
        self.status = False
        self.task = task
        # the end time of task is always the actual entering time + duration.
        self.end_time = time + task[3]

    # run when a task is finished in a processor
    def task_done(self):
        print(f"** {self.end_time} : Task {self.task[1]} completed.")
        self.status = True
        # set the task container to empty tuple
        self.task = ()


# Update time
class Clock():
    def __init__(self):
        # Attribute time to update the time of the next event
        self.time = 0
        # next_arrival_time for the time that next task enters the system
        self.next_arrival_time = 0
        '''
        Set up a list to store all the end time in processors.
        If the list is empty, it means there's no task in any processor.
        Otherwise the minimum value of the list would be the end time of
        the next finishing task.
        '''
        self.end_time_ls = []

    # get the arrival time of next task entering the system
    def get_next_arrival(self, task):
        self.next_arrival_time = task[2]

    # add the task end_time into the end_time list
    def get_next_end(self, time):
        self.end_time_ls.append(time)

    # when a task is finished in processor, delete its end_time in the end_time list
    def del_next_end(self):
        self.end_time_ls.remove(self.time)


# This class is basically the whole system
class SchedulerService():
    def __init__(self):
        # Initialization with 3 processors, 1 clock, task control and validator
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
        # print when a task enters the system
        print(
            f"** {task[2]} : "
            f"Task {task[1]} "
            f"with duration {task[3]} enters the system.")

    def get_valid_result(self, task):
        self.__valid_result = self.validator.is_valid_task(task[1])
        return self.__valid_result

    def find_processor(self, end_time):
        # to find the processor holding the first-completed task
        if self.processor1.end_time == end_time:
            return self.processor1
        elif self.processor2.end_time == end_time:
            return self.processor2
        elif self.processor3.end_time == end_time:
            return self.processor3

    def p_task_accepted(self, task):
        # print when a task is accepted by system
        print(f'** Task {task[1]} accepted.')

    def p_task_discard(self, task):
        # print when a task is discarded
        print(
            f'** Task {task[1]} '
            + 'unfeasible and discarded.')

    def p_sys_completed(self, time):
        # print when all the tasks are over, using the time that the last task ends
        print(f"** {time} : SIMULATION COMPLETED. **")

    def check(self):
        # a debugger function, to check everything's status when running the code
        print(self.processor1.task,
              self.processor2.task, self.processor3.task)
        print(self.clock.end_time_ls)
        print(self.clock.time)

    def proceed(self):
        self.p_sys_init()
        self.task.put_enter_queue(self.task_list)
        # Check if all tasks have entered the system
        while not self.enter_queue.empty():
            # Get one task from enter_queue
            self.current_task = self.enter_queue.get()
            # set the clock with the arrival time of this task
            self.clock.get_next_arrival(self.current_task)
            # if there's at least one task in the processor
            if self.clock.end_time_ls:
                '''
                If the minimum value in end_time_ls is smaller than the arrival
                time of next task, then the task would be finished in the processor
                before the new one enters the system.
                So the system should deal with the task in the processor first.
                '''
                # uncomment the line below to debug
                # self.check()
                if min(self.clock.end_time_ls) <= self.clock.next_arrival_time:
                    # put the new task back into enter_queue
                    self.enter_queue.put(self.current_task)
                    # the next event would be task finishing, update time
                    self.clock.time = min(self.clock.end_time_ls)
                    # find which processor is finishing the task
                    self.processor_found = self.find_processor(
                        self.clock.time)
                    # reset the processor and delete the end_time from the end_time list
                    self.processor_found.task_done()
                    self.clock.del_next_end()
                    '''
                    Onhold queue follows the FIFO rule.
                    If there's any task in the onhold queue,
                    the first task got into the queue would be retrieved into
                    the available processor immediately.
                    '''
                    if not self.onhold_queue.empty():
                        self.first_onhold = self.onhold_queue.get()
                        self.processor_found.proceed_task(
                            self.clock.time, self.first_onhold)
                        self.clock.get_next_end(self.processor_found.end_time)
                    '''
                    If the arrival time of next task is smaller, then the next event
                    would be the arrival of the task (entering the system)
                    Run a validation, if passed, assign it to an available processor,
                    if all the processors are busy, put it into the onhold_queue.
                    Otherwise discard the task.
                    '''
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
                '''
                If there's nothing in all the processors
                the next event will always be the task entering the system
                then proceed a validation, assign the task to processor1
                (because all the processors are available)
                '''
            else:
                # uncomment the line below to debug
                # self.check()
                self.p_enter_system(self.current_task)
                if self.get_valid_result(self.current_task):
                    self.p_task_accepted(self.current_task)
                    self.processor1.proceed_task(
                        self.current_task[2], self.current_task)
                    self.clock.get_next_end(self.processor1.end_time)
                else:
                    self.p_task_discard(self.current_task)
        '''
        After all the task in enter_queue entered the system,
        the system only needs to finish all the tasks in the processors as well
        as in the onhold_queue.
        The end_time list would be a way to know if there's still task in progress.
        The length of the list becomes 0 means all the tasks are done.
        '''
        while not len(self.clock.end_time_ls) == 0:
            # uncomment the line below to debug
            # self.check()
            # update the time to the next event
            self.clock.time = min(self.clock.end_time_ls)
            # find which processor is finishing the task
            self.processor_found = self.find_processor(
                self.clock.time)
            self.processor_found.task_done()
            self.clock.del_next_end()
            # for task in onhold_queue, get them into the available processor
            if not self.onhold_queue.empty():
                self.first_onhold = self.onhold_queue.get()
                self.processor_found.proceed_task(
                    self.clock.time, self.first_onhold)
                self.clock.get_next_end(self.processor_found.end_time)
        self.p_sys_completed(self.clock.time)


simulation = SchedulerService()
simulation.proceed()
