"""
autorec.src.check_struct

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import os
import fnmatch

def check_raw():
    """
    Check if folder containing raw images exists
    """

    folder_path = '../raw/'
    assert (os.path.isdir(folder_path)), \
        "Error: Raw images folder doesn't exist, or is at a wrong directory."

    # Check if folder is empty
    assert (len(os.listdir(folder_path)) > 0), \
        "Error: Folder which should include raw images is empty."


def check_files():
    """
    Check if current folder has all prerequisite files
    """

    # Check for toolbox_tomoDLS.py
    assert (os.path.isfile("toolbox_tomoDLS.py")), \
        "Error: toolbox_tomoDLS.py is missing."

    # Check for dm4 file
    file_list = []
    for curr_file in os.listdir('.'):
        if fnmatch.fnmatch(curr_file, '*.dm4'):
            file_list.append(curr_file)
    assert (len(file_list) > 0), \
        "Error: dm4 file not found."
    
    # Check if toolbox_stact_processed.txt exists
    assert (not os.path.isfile("toolbox_stact_processed.txt")), \
        "Error: toolbox_stact_processed.txt present. Remove it first."

    # Check if previous log exists
    for curr_file in os.listdir('.'):
        if fnmatch.fnmatch(curr_file, 'toolbox_*.log'):
            "Error: toolbox_{}.log present. Remove it first."
