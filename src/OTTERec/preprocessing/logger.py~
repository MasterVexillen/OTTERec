"""
autorec.preprocessing.logger

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 05-Mar-2021

Disclaimer: adopted and modified from toolbox_tomoDLS.py from DLS repo
"""

import threading
import datetime as dt
from autorec.preprocess.params import Params


class Logger:
    """
    Class encapsulating a Logger object
    """

    def __init__(self, params_in=None):
        """
        Initialise a Logger object

        ARGS:
        params_in (Params): input parameters (Params object)
        """

        self.lock = threading.Lock()
        self.filename_log = params_in.params['Outputs']['logfile_name']

    def __call__(self, log, stdout=True, newline=False):
        """
        Send a string to stdout and log file one process at a time.

        ARGS:
        log (str): message to be output to file
        stdout (bool): whether to output to shell
        newline (bool): whether to add new line before message
        """

        now = dt.datetime.now().strftime("%d%b%Y-%H:%M:%S")
        with self.lock:
            if newline:
                message = '\n{} - {}'.format(now, log)
            else:
                message = '{} - {}'.format(now, log)

            if stdout:
                print(message)
            with open(self.filename_log, 'a') as f:
                f.write(message + '\n')
