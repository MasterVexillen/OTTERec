"""
OTTERec.preprocessing.ctffind

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 08-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import subprocess


class CTFfind:
    """
    Class encapsulating a CTFfind object
    """

    def __init__(self, task, loggerObj, params_in):
        """
        Initialise the CTFfind object

        ARGS:
        task (list): list of tasks from worker manager
        loggerObj (Logger): Logger object for logging progress
        params_in (Params): Input parameters
        """
        self.stack, self.meta_tilt, self.inputs = task
        self.logger = loggerObj
        self.pObj = params_in
        self.params = self.pObj.params

        stack_padded = f'{self.stack:03}'
        stack_display_nb = f'stack{stack_padded}'
        path_stack = f"{self.params['Outputs']['stacks_path']}/self.stack{stack_padded}"
        filename_log = f"{path_stack}/{self.params['Outputs']['output_prefix']}_{stack_padded}_ctffind.log"

        self.filename_output = f"{path_stack}/{self.params['Outputs']['output_prefix']}_{stack_padded}_ctffind.mrc"
        self.log = f'Ctffind - {stack_display_nb}:\n'
        self.stdout = None

        # Get the image closest to 0. Only this one will be used.
        image = self.meta_tilt.loc[self.meta_tilt['tilt'].abs().idxmin(axis=0)]

        # get ctffind command and run
        os.makedirs(path_stack, exist_ok=True)

        ctf_command, ctf_input_string = self._get_ctffind(image)
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
        self.logger(self.log, nl=True)

    def _get_ctffind(self, image):
        """
        Function to return command for CTFfind

        The inputs will go through stdin. Last input: expert options=no.
        """
        cmd = [self.params['CTFfind']['CTFfind_path']]
        input_dict = [image['output'],
                      self.filename_output,
                      str(self.params['MotionCor']['desired_pixel_size']),
                      self.params['CTFfind']['voltage'],
                      self.params['CTFfind']['spherical_aberration'],
                      self.params['CTFfind']['amp_contrast'],
                      self.params['CTFfind']['amp_spec_size'],
                      self.params['CTFfind']['resolution_min'],
                      self.params['CTFfind']['resolution_max'],
                      self.params['CTFfind']['defocus_min'],
                      self.params['CTFfind']['defocus_max'],
                      self.params['CTFfind']['defocus_step'],
                      self.params['CTFfind']['Astigm_type'],
                      self.params['CTFfind']['exhaustive_search'],
                      self.params['CTFfind']['astigm_restraint'],
                      self.params['CTFfind']['phase_shift'],
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
                self.log += f'{TAB}{line}\n'
            else:
                continue
