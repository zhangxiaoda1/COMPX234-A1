import threading
import time
import random

from printDoc import printDoc
from printList import printList


class Assignment1:
    # Simulation Initialisation parameters
    NUM_MACHINES = 50  # Number of machines that issue print requests
    NUM_PRINTERS = 5  # Number of printers in the system
    SIMULATION_TIME = 30  # Total simulation time in seconds
    MAX_PRINTER_SLEEP = 3  # Maximum sleep time for printers
    MAX_MACHINE_SLEEP = 5  # Maximum sleep time for machines

    # Initialise simulation variables
    def __init__(self):
        self.sim_active = True
        self.print_list = printList()  # Create an empty list of print requests
        self.mThreads = []  # list for machine threads
        self.pThreads = []  # list for printer threads

        # Synchronisation primitives
        self.empty_slots = threading.Semaphore(self.NUM_PRINTERS)  # Counting semaphore for queue capacity (size = 5)
        self.mutex = threading.Semaphore(1)  # Binary semaphore for mutual exclusion on the queue

    def startSimulation(self):
        # Create Machine and Printer threads
        for id in range(self.NUM_MACHINES):
            thread = self.machineThread(id, self)
            self.mThreads.append(thread)
        for id in range(self.NUM_PRINTERS):
            thread = self.printerThread(id, self)
            self.pThreads.append(thread)

        # Start all the threads
        for thread in self.mThreads:
            thread.start()
        for thread in self.pThreads:
            thread.start()

        # Let the simulation run for some time
        time.sleep(self.SIMULATION_TIME)

        # Finish simulation
        self.sim_active = False

        # Wait until all printer threads finish by joining them
        for thread in self.pThreads:
            thread.join()

        print("Simulation finished.")
        # Machine threads are not joined; they will exit when sim_active becomes False.

    # Printer class
    class printerThread(threading.Thread):
        def __init__(self, printerID, outer):
            threading.Thread.__init__(self)
            self.printerID = printerID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                # Simulate printer taking some time to print the document
                self.printerSleep()
                # Grab the request at the head of the queue and print it
                self.printDox(self.printerID)

        def printerSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_PRINTER_SLEEP)
            time.sleep(sleepSeconds)

        def printDox(self, printerID):
            print(f"Printer ID: {printerID} : now available")
            # Acquire mutex to safely access the queue
            self.outer.mutex.acquire()
            # Print from the queue
            self.outer.print_list.queuePrint(printerID)
            # Release mutex
            self.outer.mutex.release()
            # Signal that a slot in the queue has become free
            self.outer.empty_slots.release()

    # Machine class
    class machineThread(threading.Thread):
        def __init__(self, machineID, outer):
            threading.Thread.__init__(self)
            self.machineID = machineID
            self.outer = outer  # Reference to the Assignment1 instance

        def run(self):
            while self.outer.sim_active:
                # Machine sleeps for a random amount of time
                self.machineSleep()
                # Machine wakes up and sends a print request
                # Wait for an empty slot in the queue
                self.outer.empty_slots.acquire()
                # Acquire mutex to safely insert into the queue
                self.outer.mutex.acquire()
                self.printRequest(self.machineID)
                # Release mutex after insertion
                self.outer.mutex.release()

        def machineSleep(self):
            sleepSeconds = random.randint(1, self.outer.MAX_MACHINE_SLEEP)
            time.sleep(sleepSeconds)

        def printRequest(self, id):
            print(f"Machine {id} Sent a print request")
            # Build a print document
            doc = printDoc(f"My name is machine {id}", id)
            # Insert it in the print queue
            self.outer.print_list.queueInsert(doc)