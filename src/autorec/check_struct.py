"""
autorec.src.check_struct

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import os
import fnmatch

def check_raw(hard_check=False):
    """
    Check if folder containing raw images exists
    """

    folder_path = '../raw/'
    if hard_check:
        if not os.path.isdir(folder_path):
            raise IOError("Error: Raw images folders not found.")
        if len(os.listdir(folder_path)) == 0:
            raise IOError("Error: Folder which should include raw images is empty.")
    else:
        if not os.path.isdir(folder_path):
            print("WARNING: Raw images folders not found.")
        if len(os.listdir(folder_path))==0:
            print("WARNING: Folder which should include raw images is empty.")

def check_files(hard_check=False):
    """
    Check if current folder has all prerequisite files
    """

    # Check for dm4 file
    file_list = []
    for curr_file in os.listdir('.'):
        if fnmatch.fnmatch(curr_file, '*.dm4'):
            file_list.append(curr_file)
    if len(file_list) == 0:
        raise IOError("Error: dm4 file not found.")

    # Check for toolbox_tomoDLS.py
    if not os.path.isfile("toolbox_tomoDLS.py"):
        raise IOError("Error: toolbox_tomoDLS.py is missing.")

    if hard_check:
        # Check if toolbox_stact_processed.txt exists
        if os.path.isfile("toolbox_stack_processed.txt"):
           raise IOError("Error: toolbox_stack_processed.txt present. Remove it first.")

