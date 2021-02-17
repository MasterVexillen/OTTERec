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
        assert (os.path.isdir(folder_path)), \
            "Error: Raw images folders not found."
        assert (len(os.listdir(folder_path)) > 0), \
            "Error: Folder which should include raw images is empty."
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
    assert (len(file_list) > 0), \
        "Error: dm4 file not found."

    # Check for toolbox_tomoDLS.py
    assert (os.path.isfile("toolbox_tomoDLS.py")), \
        "Error: toolbox_tomoDLS.py is missing."

    if hard_check:
        # Check if toolbox_stact_processed.txt exists
        assert (not os.path.isfile("toolbox_stack_processed.txt")), \
            "Error: toolbox_stack_processed.txt present. Remove it first."

