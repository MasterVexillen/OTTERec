"""
main.py

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import sys
import os
import fnmatch
import datetime as dt

import autorec.check_struct as cs
import autorec.new_inputs as ni


def get_task():
    """
    Get task from user
    """
    
    task = sys.argv[1].lower()

    allowed_tasks = [
        'check',
        'new',
        'run',
        'all',
    ]
    assert (task in allowed_tasks), \
        "Error: input task not recognised. Aborting."

    return task

def check(hard_check=False):
    """
    Perform final check for essential files
    """
    cs.check_raw(hard_check)
    cs.check_files(hard_check)

def get_today_timestamp():
    """
    Get the formatted timestamp for today
    """
    today = dt.datetime.today()
    stamp = today.strftime("%d") + today.strftime("%b") + today.strftime("%Y")

    return stamp
    
def new():
    """
    Create new input file
    """
    # Prepare gain reference
    check()
    for curr_file in os.listdir('.'):
        if fnmatch.fnmatch(curr_file, '*.dm4'):
            dm4_default = curr_file.strip('.dm4')
            break
    dm4_name = input('Name of the .dm4 file (less .dm4)? (Default: {}) '\
                     .format(dm4_default))
    if len(dm4_name) == 0:
        dm4_name = dm4_default
    dm2mrc_command = 'dm2mrc {}.dm4 gain_unflip.mrc'.format(dm4_name)
    os.system(dm2mrc_command)
    os.system('clip flipx gain_unflip.mrc gain.mrc')

    # Run toolbox_tomoDLS.py to create new default input file
    os.system('python toolbox_tomoDLS.py -c --advanced')

    timestamp = get_today_timestamp()
    inputs_name = 'Toolbox_inputs_{}.txt'.format(timestamp)
        
    # Prompt user to answer questions for changing input parameters
    user_params_dict = ni.get_params()

    # Change input file according to user preferences
    ni.change_file_params(
        file_in=inputs_name,
        qdict_in=user_params_dict,
    )

def run(timestamp_in=None):
    """
    Run toolbox_tomoDLS.py
    """
    if timestamp_in is None or len(timestamp_in)==0:
        timestamp_in = get_today_timestamp()

    # Final hard check for prerequisite files
    check(hard_check=True)
    
    # Check validity of input file with given timestamp
    inputs_name = 'Toolbox_inputs_{}.txt'.format(timestamp_in)
    assert (os.path.isfile(inputs_name)), \
        "Error in main.run: the given date doesn't have a record!"

    # Run program
    run_command = 'python toolbox_tomoDLS.py -i {}'.format(inputs_name)
    os.system(run_command)

    

def main():
    """
    Main interface of autorec
    """
    task = get_task()

    if task == 'check':
        check()

    elif task == 'new':
        check()
        new()

    elif task == 'run':
        input_timestamp = input('Use input from which date? (Please enter exactly as formatted in file name.) ')
        run(input_timestamp)

    elif task == 'all':
        check()
        new()
        run()

if __name__ == '__main__':
    main()
