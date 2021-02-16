"""
main.py

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import sys
import datetime as dt

import autorec.check_struct as cs
import autorec.new_inputs as ni


def get_task():
    task = sys.argv[1].lower()

    allowed_tasks = [
        'check',
        'new_inputs',
    ]
    assert (task in allowed_tasks), \
        "Error: input task not recognised. Aborting."

    return task

def main():
    """
    Main interface of autorec
    """
    task = get_task()

    if task == 'check':
        cs.check_raw()
        cs.check_files()

    elif task == 'new_inputs':
        today = dt.datetime.today()
        stamp = today.strftime("%d") + today.strftime("%b") + today.strftime("%Y")

        user_input = ni.get_params()
        

if __name__ == '__main__':
    main()
