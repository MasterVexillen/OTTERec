"""
OTTERec.preprocessing.worker

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 02-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py from Diamond repo
"""

from threading import Semaphore
import multiprocess
import os

from OTTERec.preprocessing.params import Params


class WorkerManager:
    """
    Class encapsulating a WorkerManager object
    """

    def __init__(self, stacks, params_in):
        """
        Initialises the WorkerManager object --- starting the pool.

        ARGS:
        stacks (list): a list of stack numbers for the stacks to be preprocessed
        params_in (Params): input parameters

        Notes:
        The size of the pool is set by the number of stacks that need to be processed and is limited by the number
        of logical cores or ad_set_max_cpus. For on-the-fly processing, most of the time only one stack is send to
        pp, therefore Stack waits for Ctffind (wait a few seconds). As such, if there is one stack, the pool will
        be set to 2 processes to run everything in parallel.
        """

        num_processes = max(len(stacks), 2)
        if num_processes > params_in.params['Run']['max_cpu']:
            num_processes = params_in.params['Run']['max_cpu']

        self.semaphore = Semaphore(num_processes)
        self.pool = multiprocess.Pool(processes=num_processes)
        self.filename_queue = params_in.hidden_queue_filename

    def new_async(self, run, task):
        """
        Start a new task, wait if all worker are busy.
        """
        self.semaphore.acquire()
        self.pool.apply_async(run, args=(task, ),
                              callback=self.task_done,
                              error_callback=self.task_failed)

    def task_done(self, _):
        """
        Called once task is done, releases the caller if blocked.
        Any output is lost: the workers should sent there log to the logger themselves.
        """
        self.semaphore.release()

    def task_failed(self, error):
        """
        When an exception is raised from a child process, terminate the pool and
        release the semaphore to prevent the main process to be stuck in self.new_async.
        This is handled by the result thread, thus raising an exception will not
        stop the program, just this thread. The pool is closed, so the main process
        will fail by itself if a new job is submitted (ValueError: Pool not running).
        """
        self.pool.close()
        self.pool.terminate()
        self.semaphore.release()
        raise error

    def close(self):
        """Wait for the processes to finish and synchronize to parent."""
        self.pool.close()
        self.pool.join()
