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

    def validate(self):
        """
        Validate parameters
        """
        # define groups for ease of reading
        inputs_group = self.params['Inputs']
        outputs_group = self.params['Outputs']
        run_group = self.params['Run']
        otf_group = self.params['On-the-fly']
        mc_group = self.params['MotionCor']
        ctf_group = self.params['CTFFind']
        brt_group = self.params['BatchRunTomo']

        # default types dictionary
        inputs_types = {
            'source_path': str,
	    'source_prefix': str,
	    'stack_field': int,
	    'tilt_angle_field': int,
	    'pixel_size': (int, float, str), # 'header' only if str
	    'source_tiffs': bool,
	    'gain_reference_file': str,
        }

        outputs_types = {
            'MotionCor2_path': str,
	    'stacks_path': str,
	    'mdocs_path': str,
	    'logfile_name': str,
	    'output_prefix': str,
        }

        run_types = {
            'max_cpu': int,
            'create_stack': bool,
            'process_stacks_list': (int, list, str), # 'all' only if str
            'rewrite': bool,
        }

        otf_types = {
            'run_otf': bool,
            'max_image': int,
            'timeout': (int, float)
        }

        mc_types = {
            'run_MotionCor2': bool,
            'MotionCor2_path': str,
            'desired_pixel_size': (int, float, str), # 'current' or 'ps_x2' if str
            'discard_frames_top': int,
            'discard_frames_bottom': int,
            'tolerance': (int, float),
            'max_iterations': int,
            'patch_size': list, # need check len==2 or 3
            'use_subgroups': bool,
            'use_gpu': (int, str), # 'auto' only if str
            'jobs_per_gpu': int,
            'gpu_memory_usage': (int, float),
        }

        ctf_types = {
            'run_ctffind': bool,
            'CTFfind_path': str,
            'voltage': (int, float),
            'spherical_aberration': (int, float),
            'amp_contrast': (int, float),
            'amp_spec_size': (int, float),
            'resolution_min': (int, float),
            'resolution_max': (int, float),
            'defocus_min': (int, float),
            'defocus_max': (int, float),
            'defocus_step': (int, float),
            'astigm_type': (str, type(None)),
            'exhaustive_search': bool,
            'astigm_restraint': bool,
            'phase_shift': (int, float)
        }

        brt_types = {
            'align_images_brt': bool,
            'adoc_file': str,
            'bead_size': (int, float),
            'init_rotation_angle': (int, float),
            'coarse_align_bin_size': (int, str), # 'auto' only if str
            'target_num_beads': int,
            'final_bin': int,
            'step_start': int,
            'step_end': int,
        }

        # Initial quick type check
        # Inputs group
        for param in inputs_types:
            if not isinstance(inputs_group[param], inputs_types[param]):
                raise TypeError(f"inputs.{param} is given as a {type(inputs_group[param])}, but it should be a {inputs_types[param]}.")
        # Outputs group
        for param in outputs_types:
            if not isinstance(outputs_group[param], outputs_types[param]):
                raise TypeError(f"outputs.{param} is given as a {type(outputs_group[param])}, but it should be a {outputs_types[param]}.")
        # Run group
        for param in run_types:
            if not isinstance(run_group[param], run_types[param]):
                raise TypeError(f"run.{param} is given as a {type(run_group[param])}, but it should be a {run_types[param]}.")
        # OTF group
        for param in otf_types:
            if not isinstance(otf_group[param], otf_types[param]):
                raise TypeError(f"otf.{param} is given as a {type(otf_group[param])}, but it should be a {otf_types[param]}.")
        # MC group
        for param in mc_types:
            if not isinstance(mc_group[param], mc_types[param]):
                raise TypeError(f"mc.{param} is given as a {type(mc_group[param])}, but it should be a {mc_types[param]}.")
        # CTF group
        for param in ctf_types:
            if not isinstance(ctf_group[param], ctf_types[param]):
                raise TypeError(f"ctf.{param} is given as a {type(ctf_group[param])}, but it should be a {ctf_types[param]}.")
        # BRT group
        for param in brt_types:
            if not isinstance(brt_group[param], brt_types[param]):
                raise TypeError(f"brt.{param} is given as a {type(brt_group[param])}, but it should be a {brt_types[param]}.")

        # Extra checks for special parameter values
        if isinstance(inputs_group['pixel_size'], str) and \
           inputs_group['pixel_size'] != 'header':
            raise ValueError("inputs.pixel_size must be 'header' or a float.")
        if isinstance(run_group['process_stacks_list'], str) and \
           run_group['process_stacks_list'] != 'all':
            raise ValueError("run.process_stacks_list must be an int, a list of ints, or 'all'.")
        if isinstance(mc_group['desired_pixel_size'], str) and \
           mc_group['desired_pixel_size'] not in ['current', 'ps_x2']:
            raise ValueError("MotionCor.desired_pixel_size must be a float, 'current' or 'ps_x2'.")
        if len(mc_group['patch_size']) != 2 and len(mc_group['patch_size']) != 3:
            raise ValueError("MotionCor.patch_size must be a list of length 2 or 3.")
        for dimension in mc_group['patch_size']:
            if not isinstance(dimension, int):
                raise TypeError("Elements of MotionCor.patch_size list must be ints.")
        if isinstance(mc_group['use_gpu'], str) and \
           mc_group['use_gpu'] != 'auto':
            raise ValueError("MotionCor.use_gpu must be an int or 'auto'.")
        if isinstance(brt_group['coarse_align_bin_size'], str) and \
           brt_group['coarse_align_bin_size'] != 'auto':
            raise ValueError("BatchRunTomo.coarse_align_bin_size must be an int or 'auto'.")


def generate_yaml(filename):
    """
    Method to generate default yaml config file

    Args:
        filename (str): name of output YAML file
    """
    default_config = {
        'Inputs': {
	    'source_path': '../raw/',
	    'source_prefix': '*',
	    'stack_field': 1,
	    'tilt_angle_field': 3,
	    'pixel_size': 'header',
	    'source_tiffs': False,
	    'gain_reference_file': 'nogain',
        },

        'Outputs': {
            'MotionCor2_path': './motioncor/',
	    'stacks_path': './stacks/',
	    'mdocs_path': './mdocs/',
	    'logfile_name': './toolbox_{}.log'.format(dt.datetime.now().strftime("%d%b%Y")),
	    'output_prefix': '*',
        },

	'Run': {
            'max_cpu': mp.cpu_count(),
            'create_stack': True,
            'process_stacks_list': 'all',
            'rewrite': True,
        },

        'On-the-fly': {
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
