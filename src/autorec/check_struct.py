"""
autorec.src.check_struct

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import os

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

    
