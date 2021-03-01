"""
autorec.preprocessing.params

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 01-Mar-2021
"""

import os
import yaml
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


def generate_yaml(filename):
    """
    Method to generate default yaml config file

    Args:
        filename (str): name of output YAML file
    """
    default_config = {
        'Inputs': {
	    'Source_path': '../raw/',
	    'Source_prefix': '*',
	    'Stack_field': 1,
	    'Tilt_angle_field': 3,
	    'Pixel_size': 'header',
	    'Source_tiffs': False,
	    'Gain_reference_file': 'nogain',
        },

        'Outputs': {
            'MotionCor2_path': './motioncor/',
	    'stacks_path': './stacks/',
	    'mdocs_path': './mdocs/',
	    'logfile_name': './toolbox_{}.log'.format(dt.datetime.now().strftime("%d%b%Y")),
	    'Output_prefix': '*',
        },

	'Run': {
            'Max_cpu': mp.cpu_count(),
            'Create_stack': True,
            'Run_rewrite': True,
        },

        'On-the-fly': {
            'Run_otf': False,
            'Max image': 37,
            'Timeout': 20,
        },

        'MotionCor': {
            'Run_MotionCor2': True,
            'MotionCor2_path': '/opt/modules/motioncor2/1.4.0/MotionCor2_1.4.0/MotionCor2_1.4.0_Cuda110',
            'Desired_pixel_size': 'ps_x2',
            'Discard_frames_top': 0,
            'Discard_frames_bottom': 1,
            'Tolerance': 0.5,
            'Max_iterations': 10,
            'Patches': [5, 5, 20],
            'Use_subgroups': True,
            'Use_gpu': 'auto',
            'Jobs_per_gpu': 3,
            'gpu_memory_usage': 0.5,
        },

        'CTFFind': {
            'Run_ctffind': True,
            'CTFfind_path': '/opt/modules/ctffind/4.1.14/bin/ctffind',
            'Voltage': 300.,
            'Spherical_aberration': 2.7,
            'Amp_contrast': 0.8,
            'Amp_spec_size': 512,
            'Min_resolution': 30.,
            'Max_resolution': 5.,
            'Min_defocus': 5000.,
            'Max_defocus': 50000.,
            'Astigm_type': None,
            'Exhaustive_search': False,
            'Astigm_restraint': False,
            'Phase_shift': 0.,
        },

        'BatchRunTomo': {
            'Align_images_brt': True,
            'adoc_file': 'default',
            'Bead_size': 10.,
            'Init_rotation_angle': 86.,
            'Coarse_align_bin_size': 'auto',
            'Target_num_beads': 25,
            'Final_bin': 5,
            'Start_step': 0,
            'End_step': 20,
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
