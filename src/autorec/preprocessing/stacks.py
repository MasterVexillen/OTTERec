"""
autorec.preprocessing.stacks

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 06-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import time
import subprocess

from autorec.preprocessing.params import Params
from autorec.preprocessing.batchruntomo import BatchRunTomo


class Stack:
    """
    Class encapsulating a Stack object.

    NOTE:
    Called by pre-processing. First create the stack and then call Batchruntomo to align it.
    The structure of this class is quite limited (__init__ needs to do
    everything) because of the way I originally organized the multiprocessing.
    I could also use __call__.
    """

    def __init__(self, task, loggerObj, params_in):
        """
        Initialise the Stack object
        Once the stack is created, call Batchruntomo to start the alignment.

        ARGS:
        task (list): list of tasks from worker manager
        loggerObj (Logger): Logger object for logging progress
        """
        self.stack, self.meta_tilt, self.inputs = task
        self.logger = loggerObj
        self.pObj = params_in
        self.params = self.pObj.params

        self.stack_padded = f"{self.stack:03}"
        self.path = f"{self.params['Outputs']['stacks_path']}/stack{self.stack_padded}/"
        self.filename_main = f"{self.params['Outputs']['output_prefix']}_{self.stack_padded}"

        self.filename_stack = self.path + self.filename_main + ".st"
        self.filename_fileinlist = self.path + self.filename_main + ".txt"
        self.filename_rawtlt = self.path + self.filename_main + ".rawtlt"

        self.log = f'Alignment - stack{self.stack_padded}:\n'

        os.makedirs(self.path, exist_ok=True)

        # To create the template for newstack and the rawtlt,
        # the images needs to be ordered by tilt angles.
        self.meta_tilt = self.meta_tilt.sort_values(by='tilt', axis=0, ascending=True)
        self._create_rawtlt()

        # run newstack
        if self.params['Run']['create_stack']:
            self._create_template_newstack()

            t1 = time.time()
            subprocess.run(self._get_newstack(),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
            t2 = time.time()
            self.log += f'{TAB}Newstack took {t2 - t1:.2f}s.\n'

        elif not os.path.isfile(self.filename_stack):
            raise FileNotFoundError(f'Stack: {self.filename_stack} is not found and Run.create_stack=0.')

        # run batchruntomo and send the logs to logger
        if self.params['BatchRunTomo']['align_images_brt']:
            batchruntomo = Batchruntomo(inputs,
                                        self.filename_stack,
                                        self.path)
            self.log += batchruntomo.log

        self.loggerObj(self.log, nl=True)

    def _create_template_newstack(self):
        """
        Create a template used by newstack fileinlist.

        template: "
        {nb_images}
        {path/of/image.mrc}
        0
        {path/of/image.mrc}
        0
        ..."
        """
        template = f"{len(self.meta_tilt)}\n" + '\n0\n'.join(self.meta_tilt['output']) + '\n0\n'
        with open(self.filename_fileinlist, 'w') as f:
            f.write(template)

    def _create_rawtlt(self):
        """
        Create .rawtlt file.

        NOTE:
        If mdoc file is not found or is not correct,
        tilts from image filenames will be used.
        """
        mdocfile = glob(f"{self.params['Outputs']['mdocs_path']}/*_{self.stack_padded}.mrc.mdoc")
        try:
            if len(mdocfile) == 0 or len(mdocfile) > 1:
                raise ValueError

            with open(mdocfile[0], 'r') as f:
                rawtlt = [float(line.replace('TiltAngle = ', '').strip('\n'))
                          for line in f if 'TiltAngle' in line]
            if len(self.meta_tilt) != len(rawtlt):
                raise ValueError
            rawtlt.sort()
            rawtlt = '\n'.join((str(i) for i in rawtlt)) + '\n'
            self.log += f'{TAB}Mdoc file: True.\n'

        # no mdoc, more than one mdoc or mdoc with missing images
        except ValueError:
            self.log += f'{TAB}Mdoc file: False.\n'
            rawtlt = '\n'.join(self.meta_tilt['tilt'].astype(str)) + '\n'

        with open(self.filename_rawtlt, 'w') as f:
            f.write(rawtlt)

    def _get_newstack(self):
        cmd = ['newstack',
               '-fileinlist', self.filename_fileinlist,
               '-output', self.filename_stack,
               '-quiet']
        return cmd
