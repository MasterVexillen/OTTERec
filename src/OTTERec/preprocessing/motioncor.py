"""
OTTERec.preprocessing.motioncor

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 05-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import os
import subprocess
import itertools


class MotionCor:
    """
    Class encapsulating a MotionCor object
    """

    def __init__(self, params_in, meta_tilt, stack, loggerObj):
        """
        Initialise a MotionCor object

        ARGS:
        params_in (Params): input parameters (Params object)
        meta_tilt (df): subset of the metadata. Describe one tilt-series.
        stack (int): tilt series number
        loggerObj (Logger): a Logger object for logging process
        """

        self.pObj = params_in
        self.params = self.pObj.params
        self.meta_tilt = meta_tilt
        self.stack = stack
        self.logger = loggerObj

        self.log = list()
        self.stack_padded = f'{self.stack:03}'
        self.log_filename = f"{self.params['Outputs']['MotionCor2_path']}/{self.params['Outputs']['output_prefix']}_{self.stack_padded}.log"
        self.first_run = True

        self._run_motioncor()

        # If ba_mc_jobs_per_gpu is too high and the device has no memory available, MotionCor
        # gives a Cufft2D error. So rerun missing images if any, but this time one per GPU.
        self.meta_tilt = self._check_motioncor_output()
        if len(self.meta_tilt) > 0:
            self.logger(f"\nMotionCor WARNING:\n"
                        f"\t{len(self.meta_tilt)} images failed. It may be because no memory was available "
                        f"on the device. You may stop the program and decrease MotionCor.jobs_per_gpu.\n"
                        f"\tReprocessing the missing images one at a time... ", newline=True)
            self._run_motioncor()

        # save output
        self._save2logfile()
        self.logger(f'MotionCor2: stack{self.stack_padded} processed.', stdout=False)

    def _run_motioncor(self):
        """
        Subroutine to run the MotionCor2 program

        ARGS:
        meta_tilt (df): subset of the metadata. Describe one tilt-series.
        """

        if self.first_run:
            jobs_per_gpu = int(self.params['MotionCor']['jobs_per_gpu'])
        else:
            jobs_per_gpu = 1
        self.first_run = False

        # Prepare generator for each image. Multiply by GPUs to allow iteration by chunks of GPUs.
        mc_commands = [self._get_command((_in, _out, _gpu))
                       for _in, _out, _gpu in zip(self.meta_tilt.raw, self.meta_tilt.output, self.meta_tilt.gpu)]

        jobs = (subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for cmd in mc_commands)

        # run subprocess by chunks of GPU
        runs, run = len(mc_commands), 0
        header = f'stack{self.stack_padded}'
        self._update_progress(runs, run, head=header)
        for job in self._yield_chunks(jobs, len(self.params['MotionCor']['use_gpu']) * jobs_per_gpu):
            # from the moment the next line is read, every process in job are spawned
            for process in [i for i in job]:
                self.log.append(process.communicate()[0].decode('UTF-8'))
                self._update_progress(runs, run, head=header, done='Motion corrected.')
                run += 1

    def _get_command(self, image):
        """
        Get commands for running MotionCor2

        ARGS:
        image (list?): image to be processed

        RETURNS:
        list
        """

        if self.params['Inputs']['source_tiffs']:
            input_motioncor = 'InTiff'
        else:
            input_motioncor = 'InMrc'

        return [self.params['MotionCor']['MotionCor2_path'],
                f'-{input_motioncor}', image[0],
                '-OutMrc', image[1],
                '-Gpu', image[2],
                '-GpuMemUsage', str(self.params['MotionCor']['gpu_memory_usage']),
                '-Gain', self.params['Inputs']['gain_reference_file'],
                '-Tol', str(self.params['MotionCor']['tolerance']),
                '-Patch', ','.join(str(i) for i in self.params['MotionCor']['patch_size']),
                '-Iter', str(self.params['MotionCor']['max_iterations']),
                '-Group', '1' if self.params['MotionCor']['use_subgroups'] else '0',
                '-FtBin', str(self.pObj.hidden_mc_ftbin),
                '-PixSize', str(self.params['Inputs']['pixel_size']),
                '-Throw', str(self.params['MotionCor']['discard_frames_top']),
                '-Trunc', str(self.params['MotionCor']['discard_frames_bottom']),
        ]

    def _check_motioncor_output(self):
        """
        Check that all the motion corrected images are where they need to be.
        Return DataFrame of raw images that need to be re-run.
        """
        return self.meta_tilt.loc[~self.meta_tilt['output'].apply(lambda x: os.path.isfile(x))]

    def _save2logfile(self):
        """
        Gather stdout of every image in one single log file
        """
        with open(self.log_filename, 'a') as log:
            log.write('\n'.join(self.log))

    @staticmethod
    def _yield_chunks(iterable, size):
        iterator = iter(iterable)
        for first in iterator:
             yield itertools.chain([first], itertools.islice(iterator, size - 1))

    @staticmethod
    def _update_progress(runs, run, head, done=None):
        """
        Simple progress bar.

        ARGS:
        runs (int):    Total number of iterations.
        run (int):     Current iteration.
        head (str):    String to print before the bar.
        done (str):    String to print at 100%.
        """
        bar_length = 15
        progress = (run + 1) / runs if run else 0
        if progress >= 1:
            progress = 1
            status = f"{done}\r\n"
        else:
            status = "Corrected..."
        block = int(round(bar_length * progress, 0))
        bar = "#" * block + "-" * (bar_length - block)
        text = f"\r{head}: [{bar}] {round(progress * 100)}% {status}"
        print(text, end='')
