"""
OTTERec.preprocessing.metadata

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 02-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import subprocess
from glob import glob

import pandas as pd
import numpy as np


class Metadata:
    """
    Class encapsulating a Metadata object
    """

    def __init__(self, paramsObj, loggerObj):
        """
        Initialising a Metadata object

        ARGS:
        paramsObj (Params): Params object containing input parameters
        loggerObj (Logger): Logger object for logging progress
        """
        self.pObj = paramsObj
        self.params = self.pObj.params
        self.stacks_nb = None
        self.stacks_tilt = None
        self.images_per_stack = None

        self.logger = loggerObj

        # Set path to raw files
        if self.params['MotionCor']['run_MotionCor2']:
            self.path = self.params['Inputs']['source_path']
            self.extension = 'tif'
        else:
            self.path = self.params['Outputs']['motionCor2_path']
            self.extension = 'mrc'

    def get_metadata(self):
        """
        Gather metadata and return it in one DataFrame.
        """
        meta = self._collect_raw_files()
        meta = meta.sort_values(by='nb', axis=0, ascending=True)

        self.stacks_len = len(meta)
        self.stacks_nb = meta['nb'].unique()
        self.stacks_images_per_stack = ', '.join((str(i)
                                                  for i in set((len(meta[meta['nb'] == stack])
                                                                for stack in self.stacks_nb))))
        # set output file name and assign every image to one GPU
        if self.params['MotionCor']['run_MotionCor2']:
            meta['gpu'] = self._get_gpu_id()
            output_str = f"{self.params['Outputs']['MotionCor2_path']}/{self.params['Outputs']['output_prefix']}_{row['nb']:03}_{row['tilt']}.mrc"
            meta['output'] = meta.apply(
                lambda row: output_str, axis=1)
        else:
            meta['output'] = meta['raw']

        return meta

    def save_processed_stack(self):
        """
        Save in a text file the stacks that were processed.
        """
        with open(self.pObj.hidden_queue_filename, 'a') as f:
            f.write('\n:' + ':'.join((str(i) for i in self.stacks_nb)) + ':')

    def _collect_raw_files(self):
        """
        Function to collect files and compile into a single pandas dataframe for processing

        RETURNS:
        pandas DataFrame
        """
        raw_files = glob('{}/{}*.{}'.format(self.path,
                                            self.params['Inputs']['source_prefix'],
                                            self.extension)
        )
        if len(raw_files) == 0:
            raise IOError("Error in metadata.Metadata._collect_raw_files: Files not found.")

        raw_files, raw_files_nb, raw_files_tilt = self._clean_raw_files(raw_files)
        if not raw_files:
            self.logger('Nothing to process (maybe it is already processed?).')
            exit()

        return pd.DataFrame(dict(raw=raw_files, nb=raw_files_nb, tilt=raw_files_tilt))

    def _clean_raw_files(self, file_list):
        """
        Function to remove unwanted stacks

        ARGS:
        file_list (list): a list of raw file names

        RETURNS:
        cleaned: Selected raw files.
        cleaned_nb: Stack numbers of the corresponding raw_files_cleaned.
        cleaned_tilt: Tilt angles of the corresponding raw_files_cleaned.

        NOTE:
        First apply a restriction on which stack to keep for processing:
            There are two possible restrictions:
                - ad_run_nb: positive restriction; process only these specified stacks.
                - toolbox.queue: negative restriction; do not process these stacks.

            The negative restriction is the priority restriction and can be deactivated
            using ad_run_overwrite. In any case, it should only be ran when --fly is False
            because OnTheFly already check for the toolbox_stack_processed.txt.

            Both restrictions are a list of integers (stack nb) or an empty list if no restriction found.

        Then, structure the raw files to feed to pd.DataFrame.
        """

        # Remove stacks in stack_to_remove list
        if self.params['Run']['run_rewrite'] or \
           self.params['Run']['run_otf']:
            stack_to_remove = list()
        else:
            stack_to_remove = self._exclude_stacks()

        # File cleaning
        cleaned, cleaned_nb, cleaned_tilt = list(), list(), list()
        for curr_file in file_list:
            filename_split = curr_file.split('/')[-1].split('_')
            try:
                stack_nb = int(''.join(i for i in filename_split[self.inputs.ba_set_field_nb] if i.isdigit()))
            except IndexError or ValueError as err:
                raise IndexError(f'Clean files (nb): {err}')

            # first check that the stack was not processed already
            if stack_nb in stack_to_remove:
                continue

            # Then check that the stack is one of the stack that should be processed.
            # If self.inputs.ad_run_nb is empty, then positive restriction is not applied.
            if len(self.params['Run']['process_stacks_list']) > 0 and \
               stack_nb not in self.params['Run']['process_stacks_list']:
                continue

            cleaned.append(curr_file)
            cleaned_nb.append(stack_nb)
            try:
                file_tilt = filename_split[self.params['Inputs']['tilt_angle_field']].replace(
                    f'.{self.extension}', '').replace('[', '').replace(']', '')
                cleaned_tilt.append(float(file_tilt))
            except IndexError or ValueError as err:
                raise IndexError(f'Clean files (tilt): {err}')

        return cleaned, cleaned_nb, cleaned_tilt

    def _exclude_stacks(self):
        """
        Catch every stack that was already processed (saved in inputs.hidden_queue_filename).
        """
        stack_to_remove = []
        try:
            with open(self.pObj.hidden_queue_filename, 'r') as f:
                remove_stack = f.readlines()

            if remove_stack:
                for line in remove_stack:
                    line = [int(i) for i in line.strip('\n').strip(' ').strip(':').split(':') if i != '']
                    stack2remove += line

            return stack2remove

        # first time running
        except IOError:
            return stack2remove

    def _get_gpu_id(self):
        """
        Set a GPU to an image.
        For each tilt-series, the images are dispatched across the visible GPUs.

        RETURNS:
        list
        """
        if self.params['Run']['run_otf']:
            # Used for otf: every time pp is called, it must recompute the available GPUs.
            # Thus it needs to remember the original input.
            self.params['MotionCor']['use_gpu'] = self.pObj.hidden_oft_gpu

        # catch GPU
        if self.params['MotionCor']['use_gpu'] == 'auto':
            self.params['MotionCor']['use_gpu'] = self._get_gpu_from_nvidia_smi()
        else:
            try:
                self.params['MotionCor']['use_gpu'] = [int(gpu) for gpu in self.inputs.ba_mc_gpu.split(',')]
            except ValueError:
                raise ValueError("Get GPU: ba_mc_gpu must be an (list of) integers or 'auto'")

        # map to DataFrame
        mc_gpu = [str(i) for i in self.self.params['MotionCor']['use_gpu']] * \
            np.ceil(self.stacks_len / len(self.params['MotionCor']['use_gpu']))
        len_diff = len(mc_gpu) - self.stacks_len
        if len_diff:
            mc_gpu = mc_gpu[:-len_diff]

        return mc_gpu

    @staticmethod
    def _get_gpu_from_nvidia_smi():
        """
        Catch available GPUs using nvidia-smi.
        It could be much faster using pyCUDA or something similar, but I want to limit
        the number of library to install for the user.
        """
        nv_uuid = subprocess.run(['nvidia-smi', '--list-gpus'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='ascii')
        nv_processes = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_uuid', '--format=csv'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='ascii')

        # catch the visible GPUs
        if nv_uuid.returncode != 0 or nv_processes.returncode != 0:
            raise AssertionError(f'Error in metadata._get_gpu_from_nvidia_smi: nvidia-smi returned an error: {nv_uuid.stderr}')
        else:
            nv_uuid = nv_uuid.stdout.strip('\n').split('\n')
            visible_gpu = list()
            for gpu in nv_uuid:
                id_idx = gpu.find('GPU ')
                uuid_idx = gpu.find('UUID')

                gpu_id = gpu[id_idx + 4:id_idx + 6].strip(' ').strip(':')
                gpu_uuid = gpu[uuid_idx + 5:-1].strip(' ')

                # discard the GPU hosting a process
                if gpu_uuid not in nv_processes.stdout.split('\n'):
                    visible_gpu.append(gpu_id)

        if visible_gpu:
            return visible_gpu
        else:
            raise ValueError(f'Error in metadata._get_gpu_from_nvidia_smi: {len(nv_uuid)} GPU detected, but none of them is free.')
