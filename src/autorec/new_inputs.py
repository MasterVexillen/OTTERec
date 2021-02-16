"""
autorec.new_inputs.py

Author: Neville B.-y. Yee
Date: 16-Feb-2021

Version: 0.1
"""

import os

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

    mc_motioncor = input("Path to Motioncor2? (Default: /opt/modules/motiorn2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_cuda110) ")
    if len(mc_motioncor) == 0:
        mc_motioncor = '/opt/modules/motiorn2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_cuda110)'

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
    
    return (prefix_find, prefix_add, path_raw, mcor, stacks, mdocs,
            run_mcor, run_ctffind, run_stack, run_batchruntomo, run_otf,
            run_overwrite, mc_motioncor, ctf_ctffind,
            mc_throw, mc_tif, mc_gain)
