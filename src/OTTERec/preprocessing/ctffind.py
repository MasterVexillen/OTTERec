"""
OTTERec.preprocessing.ctffind

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 08-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import os
import subprocess


class CTFfind:
    """
    Class encapsulating a CTFfind object
    """

    def __init__(self, inputs):
        """
        Initialise the CTFfind object

        ARGS:
        inputs (tuple): (task, logger, params)
        """
        self.stack, self.meta_tilt, self.inputs = inputs[0]
        self.logger = inputs[1]
        self.params = self.inputs.params

        stack_padded = f'{self.stack:03}'
        stack_display_nb = f'stack{stack_padded}'
        path_stack = f"{self.params['Outputs']['stacks_path']}/stack{stack_padded}"
        filename_log = f"{path_stack}/{self.params['Outputs']['output_prefix']}_{stack_padded}_ctffind.log"

        self.filename_output = f"{path_stack}/{self.params['Outputs']['output_prefix']}_{stack_padded}_ctffind.mrc"
        self.log = f'Ctffind - {stack_display_nb}:\n'
        self.stdout = None

        # Get the image closest to 0. Only this one will be used.
        self.image = self.meta_tilt.loc[self.meta_tilt['tilt'].abs().idxmin(axis=0)]

        # get ctffind command and run
        os.makedirs(path_stack, exist_ok=True)

        ctf_command, ctf_input_string = self._get_ctffind()
        ctffind_run = subprocess.run(ctf_command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     input=ctf_input_string,
                                     encoding='ascii')

        if ctffind_run.stderr:
            raise ValueError(f'Ctffind: An error has occurred ({ctffind_run.returncode}) '
                             f'on stack{stack_padded}.')
        else:
            self.stdout = ctffind_run.stdout

        # save stdout
        with open(filename_log, 'w') as f:
            f.write(self.stdout)

        # send the logs back to main
        self._get_ctffind_log()
        self.logger(self.log, newline=True)

    def _get_ctffind(self):
        """
        Function to return command for CTFfind

        The inputs will go through stdin. Last input: expert options=no.
        """
        cmd = [self.params['CTFFind']['CTFfind_path']]
        input_dict = [self.image['output'],
                      self.filename_output,
                      str(self.params['MotionCor']['desired_pixel_size']),
                      str(self.params['CTFFind']['voltage']),
                      str(self.params['CTFFind']['spherical_aberration']),
                      str(self.params['CTFFind']['amp_contrast']),
                      str(self.params['CTFFind']['amp_spec_size']),
                      str(self.params['CTFFind']['resolution_min']),
                      str(self.params['CTFFind']['resolution_max']),
                      str(self.params['CTFFind']['defocus_min']),
                      str(self.params['CTFFind']['defocus_max']),
                      str(self.params['CTFFind']['defocus_step']),
                      str(self.params['CTFFind']['astigm_type']) if self.params['CTFFind']['astigm_type'] else 'no',
                      'yes' if self.params['CTFFind']['exhaustive_search'] else 'no',
                      'yes' if self.params['CTFFind']['astigm_restraint'] else 'no',
                      'yes' if self.params['CTFFind']['phase_shift'] else 'no',
                      'no']

        input_string = '\n'.join(input_dict)
        return cmd, input_string


    def _get_ctffind_log(self):
        """
        Format the stdout of Ctffind and save it as a str.
        """
        look4 = ['MRC data mode',
                 'Bit depth',
                 'Estimated defocus values',
                 'Estimated azimuth of astigmatism',
                 'Score',
                 'Thon rings with good fit up to',
                 'CTF aliasing apparent from']
        possible_lines = filter(lambda i: i != '', self.stdout.split('\n'))

        for line in possible_lines:
            if any(item in line for item in look4):
                self.log += f'\t{line}\n'
            else:
                continue
