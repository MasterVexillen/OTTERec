"""
autorec.preprocessing.params

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 01-Mar-2021
"""

import os
import sys
import yaml
from glob import glob
import pandas as pd
import multiprocess as mp
import datetime as dt


class Params:
    """
    Class encapsulating Param objects
    """

    def __init__(self, param_in=None):
        """
        Initialising a Param object
        """
        self.params = param_in

        self.hidden_oft_gpu = None  # see Metadata._get_gpu_id
        self.hidden_mc_ftbin = None  # see self.set_pixelsize
        self.hidden_queue_filename = 'toolbox_stack_processed.txt'
        self.hidden_run_nb = None  # just for warning, remember positive restriction


def generate_yaml(filename):
    """
    Method to generate default yaml config file

    Args:
        filename (str): name of output YAML file
    """
    default_config = {
        'inputs': {
	    'source_path': '../raw/',
	    'source_prefix': '*',
	    'stack_field': 1,
	    'tilt_angle_field': 3,
	    'pixel_size': 'header',
	    'source_tiffs': False,
	    'gain_reference_file': 'nogain',
        },

        'outputs': {
            'MotionCor2_path': './motioncor/',
	    'stacks_path': './stacks/',
	    'mdocs_path': './mdocs/',
	    'logfile_name': './toolbox_{}.log'.format(dt.datetime.now().strftime("%d%b%Y")),
	    'output_prefix': '*',
        },

	'run': {
            'max_cpu': mp.cpu_count(),
            'create_stack': True,
            'process_stacks_list': 'all',
            'rewrite': True,
        },

        'on-the-fly': {
            'run_otf': False,
            'max_image': 37,
            'timeout': 20,
        },

        'MotionCor': {
            'run_MotionCor2': True,
            'MotionCor2_path': '/opt/modules/motioncor2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_Cuda110',
            'desired_pixel_size': 'ps_x2',
            'discard_frames_top': 0,
            'discard_frames_bottom': 1,
            'tolerance': 0.5,
            'max_iterations': 10,
            'patch_size': [5, 5, 20],
            'use_subgroups': True,
            'use_gpu': 'auto',
            'jobs_per_gpu': 3,
            'gpu_memory_usage': 0.5,
        },

        'CTFFind': {
            'run_ctffind': True,
            'CTFfind_path': '/opt/modules/ctffind/4.1.14/bin/ctffind',
            'voltage': 300.,
            'spherical_aberration': 2.7,
            'amp_contrast': 0.8,
            'amp_spec_size': 512,
            'resolution_min': 30.,
            'resolution_max': 5.,
            'defocus_min': 5000.,
            'defocus_max': 50000.,
            'defocus_step': 500.,
            'astigm_type': None,
            'exhaustive_search': False,
            'astigm_restraint': False,
            'phase_shift': 0.,
        },

        'BatchRunTomo': {
            'align_images_brt': True,
            'adoc_file': 'default',
            'bead_size': 10.,
            'init_rotation_angle': 86.,
            'coarse_align_bin_size': 'auto',
            'target_num_beads': 25,
            'final_bin': 5,
            'step_start': 0,
            'step_end': 20,
        }
    }

    with open(filename, 'w') as f:
        yaml.dump(default_config, f, indent=4, sort_keys=False)


def read_yaml(filename):
    """
    Read in a YAML config file

    Args:
        filename (str): name of YAML file to be read

    Returns:
        Params object
    """
    if not os.path.isfile(filename):
        raise IOError("Error in preprocessing.params.read_yaml: File not found.")

    with open(filename, 'r') as f:
        params = yaml.load(f, Loader=yaml.FullLoader)

    return Params(params)


def params_lookup():
    """
    Subroutine to search for parameters and prints out info
    """

    assert len(sys.argv)==2, \
        "Invalid input. USAGE: autorec.lookup parameter"

    user_param = sys.argv[1]

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    params_list = pd.read_csv(curr_dir+"/data/params_list.csv")

    # Initial check if input parameter is valid
    if '.' in user_param:
        lookup_key = user_param.split(sep='.')
        # Check format
        if len(lookup_key) != 2:
            raise ValueError("Error in params_lookup: Wrong format of input parameter.")
        # Check validity of input parameters
        lookup_group, lookup_name = lookup_key
        params_list['group_lower'] = params_list['new_params_group'].map(lambda x: x.lower())
        params_list['name_lower'] = params_list['new_params'].map(lambda x: x.lower())
        if lookup_group.lower() not in params_list['group_lower'].unique() or \
           lookup_name.lower() not in params_list['name_lower'].unique():
            raise ValueError("Group or name of parameter not found.")
        # Now parameter is validated
        param_is_new = True

    else:
        # Assume parameter is in old format
        lookup_key = user_param
        if lookup_key.lower() not in params_list['old_params'].unique():
            raise ValueError("Parameter not found.")
        param_is_new = False

    # Lookup data
    if not param_is_new:
        old_param = user_param
        data_row = params_list[params_list['old_params']==old_param]
        new_param_group = data_row.new_params_group.item()
        new_param_name = data_row.new_params.item()
        data_type = data_row.data_type.item()
        description = data_row.description.item()
    else:
        data_row = params_list[(params_list['group_lower']==lookup_group.lower()) &
                               (params_list['name_lower']==lookup_name.lower())]

    # Print out information
    print("\nNew parameter in YAML (format: GROUP.NAME):")
    print(f"{data_row['new_params_group'].values[0]}.{data_row['new_params'].values[0]} \n")
    print("Old parameter:")
    print(f"{data_row['old_params'].values[0]} \n")
    print("Description:")
    print(f"{data_row['description'].values[0]} \n")
    print("Data type(s):")
    print(f"{data_row['data_type'].values[0]} \n")
    print("Default value: ")
    print(f"{data_row['default_value'].values[0]}\n")
