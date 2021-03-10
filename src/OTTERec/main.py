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

import OTTERec.check_struct as cs
import OTTERec.new_inputs as ni
import OTTERec.preprocessing.params as params
import OTTERec.preprocessing.logger as logger
import OTTERec.preprocessing.otf as otf
import OTTERec.preprocessing.preprocessing as pp


LOGO = f"""
                                  .----.__
                                 / c  ^  _`;
                                 |     .--'
       OOOOOOO         TTTTT      \   (                     RRRRRRRRRRR
     OOOOOOOOOO       TTTTT       /  -.\                    RRRRRRRRRRRRR
    OOOO    OOOO   TTTTTTTTTTT   / .    \         EEEEEE    RRRR     RRRRR     EEEEEE        CCCCCC   
   OOOO      OOO  TTTTTTTTTTT   /  \    |       EEEEEEEEE   RRRR      RRRR   EEEEEEEEE     CCCCCCCCC  
  OOOO       OOO TTTTTTTTTTT   ;    `-. `.     EEEE    EEE  RRRR     RRRR   EEEE    EEE   CCCC    CCC 
  OOO        OOO   TTTTT       |      /`'.`.  EEEE     EEEE RRRRRRRRRRRR   EEEE     EEEE CCCC     CCCC
  OOO        OOO  TTTTT        |      |   \ \ EEEEEEEEEEEEE RRRRRRRRRR     EEEEEEEEEEEEE CCCC         
  OOOO      OOOO TTTTT    TTT  |    __|    `' EEEE          RRRR    RRR    EEEE          CCCC         
  OOOOO    OOOO   TTTTT  TTT   ;   /   \      EEEE    EEEE  RRRR    RRRR   EEEE    EEEE  CCCC    CCCC 
   OOOOOOOOOOO     TTTTTTTT   ,'        |      EEEEEEEEEE   RRRR     RRRR   EEEEEEEEEE    CCCCCCCCCC  
     OOOOOO         TTTTT    (_`'---._ /--,     EEEEEEEE    RRRR      RRRR   EEEEEEEE      CCCCCCCC   
                               `'---._`'---..__
                                      `''''--, )
                                        _.-'`,`
                                         ````
"""


def check():
    """
    Perform final check for essential files
    """
    hard_check = input('Perform hard check? ([y]/n) ').lower()
    if len(hard_check)==0 or hard_check == 'y':
        hard_check = True
    elif hard_check == 'n':
        hard_check = False
    else:
        raise ValueError('Error in check: Invalid input.')

    cs.check_raw(hard_check)
    cs.check_files(hard_check)

def get_today_timestamp():
    """
    Get the formatted timestamp for today
    """
    today = dt.datetime.today()
    stamp = today.strftime("%d") + today.strftime("%b") + today.strftime("%Y")

    return stamp

# def new():
#     """
#     Create new input file
#     """
#     # Prepare gain reference
#     check()
#     for curr_file in os.listdir('.'):
#         if fnmatch.fnmatch(curr_file, '*.dm4'):
#             dm4_default = curr_file.strip('.dm4')
#             break
#     dm4_name = input('Name of the .dm4 file (less .dm4)? (Default: {}) '\
#                      .format(dm4_default))
#     if len(dm4_name) == 0:
#         dm4_name = dm4_default
#     dm2mrc_command = 'dm2mrc {}.dm4 gain_unflip.mrc'.format(dm4_name)
#     os.system(dm2mrc_command)
#     os.system('clip flipx gain_unflip.mrc gain.mrc')

#     # Run toolbox_tomoDLS.py to create new default input file
#     os.system('python toolbox_tomoDLS.py -c --advanced')

#     timestamp = get_today_timestamp()
#     inputs_name = 'Toolbox_inputs_{}.txt'.format(timestamp)

#     # Prompt user to answer questions for changing input parameters
#     user_params_dict = ni.get_params()

#     # Change input file according to user preferences
#     ni.change_file_params(
#         file_in=inputs_name,
#         qdict_in=user_params_dict,
#     )

def run():
    """
    Run toolbox_tomoDLS.py
    """
    # Perform hard check first
    check()

    timestamp_in = input('Use input from which date? (Please enter exactly as formatted in file name.) ')
    if timestamp_in is None or len(timestamp_in)==0:
        timestamp_in = get_today_timestamp()

    # Check validity of input file with given timestamp
    inputs_name = 'Toolbox_inputs_{}.txt'.format(timestamp_in)
    assert (os.path.isfile(inputs_name)), \
        "Error in main.run: the given date doesn't have a record!"

    # Run program
    run_command = 'python toolbox_tomoDLS.py -i {}'.format(inputs_name)
    os.system(run_command)

def new_revamp():
    """
    Generate YAML config file
    """
    # Prepare gain reference
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

    if len(sys.argv) != 2:
        raise ValueError("Error in input length. USAGE: OTTERec.new YAML")

    yaml_name = sys.argv[1]
    params.generate_yaml(yaml_name)

def validate_revamp():
    """
    Validate YAML config file
    """
    if len(sys.argv) != 2:
        raise ValueError("Error in input length. USAGE: OTTERec.validate YAML")

    yaml_name = sys.argv[1]
    yaml_params = params.read_yaml(yaml_name)
    yaml_params.validate()
    print("Input YAML config file validated. All parameters are of the correct data types.")

def run_revamp():
    """
    Run all preprocessing procedures
    """

    print(LOGO)

    if len(sys.argv) != 2:
        raise ValueError("Error in input length. USAGE: OTTERec.run YAML")

    yaml_name = sys.argv[1]
    yaml_params = params.read_yaml(yaml_name)
    run_logger = logger.Logger(yaml_params)

    task_bar = f"""
    ==============================
    -------      TASKS     -------
    ==============================
    """

    log_bar = f"""
    ==============================
    -------       LOG      -------
    ==============================
    """

    print(task_bar)
    print(f"MotionCor2:   {yaml_params.params['MotionCor']['run_MotionCor2']}\n"
          f"Ctffind:      {yaml_params.params['CTFFind']['run_ctffind']}\n"
          f"New stack:    {yaml_params.params['Run']['create_stack']}\n"
          f"Batchruntomo: {yaml_params.params['BatchRunTomo']['align_images_brt']}\n\n")
    print(log_bar      )

    if yaml_params.params['On-the-fly']['run_otf']:
        print(f"On-the-fly processing: (Tolerated inactivity: {yaml_params.params['On-the-fly']['timeout']}min).")
        run_otf = otf.OnTheFly(yaml_params)
        run_otf.run(yaml_params)
    else:
        pp.preprocessing(yaml_params, run_logger)
