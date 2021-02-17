"""
autorec.new_inputs.py

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import os
import re

def get_params():
    """
    Prompt user to give essential parameters
    """

    prefix_find = input("Prefix to look for? ")
    assert len(prefix_find) > 0, \
        "Error in get_params: Prefix must be a non-empty string."

    prefix_add = input("Prefix to add? (Default: {}) ".format(prefix_find))
    if len(prefix_add) == 0:
        prefix_add = prefix_find

    stack_field_in = input("Field # for stack numbers? (Default: 1) ")
    if len(stack_field_in) == 0:
        stack_field = 1
    else:
        stack_field = int(stack_field_in)

    tilt_field_in = input("Field # for tilt angles? (Default: 3) ")
    if len(tilt_field_in) == 0:
        tilt_field = 3
    else:
        tilt_field = int(tilt_field_in)

    px_size = input("Pixel size of raw images? (Default: header) ")
    if len(px_size) == 0:
        px_size = 'header'
    else:
        px_size = float(px_size)

    jobs_per_gpu = input("Jobs per GPU? (Default: 1) ")
    if len(jobs_per_gpu) == 0:
        jobs_per_gpu = 1
    else:
        jobs_per_gpu = int(jobs_per_gpu)

    path_raw = input("Path to raw images? (Default: ../raw/{}_*) ".format(prefix_find))
    if len(path_raw) == 0:
        path_raw =  '../raw/' + prefix_find + '_*'

    mcor = input("Folder name for MotionCor? (Default: motioncor) ")
    if len(mcor) == 0:
        mcor = 'motioncor'

    stacks = input("Folder name for stacks? (Default: stacks) ")
    if len(stacks) == 0:
        stacks = 'stacks'

    mdocs = input("Folder name for mdoc files? (Default: mdocs) ")
    if len(mdocs) == 0:
        mdocs = 'mdocs'

    run_mcor_in = input("Run MotionCor2? ([y]/n) ").lower()
    if run_mcor_in == 'y' or len(run_mcor_in) == 0:
        run_mcor = 1
    elif run_mcor_in == 'n':
        run_mcor = 0
    else:
        raise ValueError("Invalid input for run_motioncor.")
        
    run_ctffind_in = input("Run CTFFind? ([y]/n) ").lower()
    if run_ctffind_in == 'y' or len(run_ctffind_in) == 0:
        run_ctffind = 1
    elif run_ctffind_in == 'n':
        run_ctffind = 0
    else:
        raise ValueError("Invalid input for run_ctffind.")

    run_stack_in = input("Run stack? ([y]/n) ").lower()
    if run_stack_in == 'y' or len(run_stack_in) == 0:
        run_stack = 1
    elif run_stack_in == 'n':
        run_stack = 0
    else:
        raise ValueError("Invalid input for run_stack.")
    
    run_batchruntomo_in = input("Run batchruntomo? ([y]/n) ").lower()
    if run_batchruntomo_in == 'y' or len(run_batchruntomo_in) == 0:
        run_batchruntomo = 1
    elif run_batchruntomo_in == 'n':
        run_batchruntomo = 0
    else:
        raise ValueError("Invalid input for run_batchruntomo.")

    run_otf_in = input("Run on-the-fly? (y/[n]) ").lower()
    if run_otf_in == 'y':
        run_otf = 1
    elif run_otf_in == 'n' or len(run_otf_in)==0:
        run_otf = 0
    else:
        raise ValueError("Invalid input for run_onthefly.")
    
    overwrite_in = input("Overwrite data? (y/[n]) ").lower()
    if overwrite_in == 'y':
        run_overwrite = 1
    elif overwrite_in == 'n' or len(overwrite_in)==0:
        run_overwrite = 0
    else:
        raise ValueError("Invalid input for run_overwrite.")

    mc_motioncor = input("Path to Motioncor2? (Default: /opt/modules/motioncor2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_Cuda110) ")
    if len(mc_motioncor) == 0:
        mc_motioncor = '/opt/modules/motioncor2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_Cuda110'

    ctf_ctffind = input("Path to CTFFind? (Default: /opt/modules/ctffind/4.1.14/bin/ctffind) ")
    if len(ctf_ctffind) == 0:
        ctf_ctffind = '/opt/modules/ctffind/4.1.14/bin/ctffind'

    mc_throw_in = input("Frame to remove? (Default: 1) ")
    if len(mc_throw_in) == 0:
        mc_throw = 1
    else:
        mc_throw = int(mc_throw_in)

    mc_tif_in = input("Are raw files TIFs? ([y]/n) ").lower()
    if mc_tif_in == 'y' or len(mc_tif_in) == 0:
        mc_tif = 1
    elif mc_tif_in == 'n':
        mc_tif = 0
    else:
        raise ValueError("Invalid input for mc_tif.")

    mc_gain = input("Name of gain file? (Default: gain.mrc) ")
    if len(mc_gain) == 0:
        mc_gain = 'gain.mrc'


    # Set dictionary to be returned
    question_dict = {
        "ba_set_prefix2look4": prefix_find,
        "ba_set_prefix2add": prefix_add,
        "ba_set_field_nb": stack_field,
        "ba_set_field_tilt": tilt_field,
        "ba_set_pixelsize": px_size,
        "ba_path_raw": path_raw,
        "ad_path_motioncor": mcor,
        "ad_path_stacks": stacks,
        "ad_path_mdocfiles": mdocs,
        "ba_run_motioncor": run_mcor,
        "ba_run_ctffind": run_ctffind,
        "ba_run_stack": run_stack,
        "ba_run_batchruntomo": run_batchruntomo,
        "ba_run_onthefly": run_otf,
        "ad_run_overwrite": run_overwrite,
        "ba_mc_motioncor": mc_motioncor,
        "ba_ctf_ctffind": ctf_ctffind,
        "ad_mc_throw": mc_throw,
        "ba_mc_tif": mc_tif,
        "ba_mc_gain": mc_gain,
        }
        
    return question_dict


def change_file_params(file_in, qdict_in):
    """
    Change parameters in input file according to user's preferences
    """

    # Check file is valid
    assert(os.path.isfile(file_in)), \
        "Error in new_inputs.change_params: File not found."

    # Check user dictionary is valid
    assert(isinstance(qdict_in, dict) and \
           len(qdict_in) > 0), \
           "Error in new_inputs.change_params: Input dictionary not valid or empty."

    # Read file
    with open(file_in, 'r') as f:
        source = f.readlines()

    # Overwrite parameters
    with open(file_in, 'w') as f:
        for line in source:
            for key in qdict_in:
                pattern = r'({}=)\S*'.format(key)
                if match := re.match(pattern, line):
                    f.write(match.group(1) + str(qdict_in[key]) + '\n')
                    break
            else:
                f.write(line)
                f.truncate()
