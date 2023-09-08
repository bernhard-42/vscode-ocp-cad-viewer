# SuperFastPython.com
# example of parent terminating itself and child remains running
from time import sleep
from multiprocessing import Process
from multiprocessing import parent_process
import os
import signal


# task executed in a child process
def task():
    os.kill(os.getppid(), signal.SIGTERM)

    for i in range(10):
        # report a message
        # print("Task is running...", flush=True)
        # block for a moment
        sleep(1)
        # get the parent process
    parent = parent_process()

    # check if the main process is still running
    print(f"Parent alive: {parent.is_alive()}")


# protect the entry point
if __name__ == "__main__":
    # create and configure a child process
    process = Process(target=task)
    process.deamon = True
    # start the child process
    process.start()

    # report a final message
    print("Main is done")
    # terminate self
