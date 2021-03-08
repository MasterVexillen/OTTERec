"""
OTTERec.preprocessing.otf

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 08-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

from glob import glob
import pandas as pd


class OnTheFly:
    """
    Class encapsulating an OnTheFly object
    """

    def __init__(self, paramsObj):
        """
        Initialise an OnTheFly object

        ARGS:
        paramsObj (Params): a Params object containing all parameters
        """
        self.pObj = paramsObj
        self.params = self.pObj.params

        if self.params['MotionCor']['run_MotionCor2']:
            self.path = self.params['Inputs']['source_path']
        else:
            self.path = self.params['Outputs']['MotionCor2_path']
        self.prefix = self.params['Inputs']['source_prefix']
        if self.params['Inputs']['source_tiffs'] and self.params['MotionCor']['run_MotionCor2']:
            self.extension = 'tif'
        else:
            self.extension = 'mrc'
        self.field_nb = self.params['Inputs']['stack_field']

        # refresh
        self.time_between_checks = 5

        # Queue of stacks. Processed stacks are saved and not reprocessed.
        self.queue_filename = self.pObj.hidden_queue_filename
        if not self.params['Run']['run_rewrite']:
            self.processed = self._exclude_queue()
        else:
            self.processed = list()
        self.queue = None

        # tolerate some inactivity
        self.buffer = 0
        try:
            self.buffer_tolerance_sec = int(self.params['On-the-fly']['timeout']) * 60
        except ValueError as err:
            raise ValueError(f'On-the-fly: {err}')
        self.buffer_tolerance = self.buffer_tolerance_sec // self.time_between_checks

        # catch the available raw files
        self.data = None
        self.data_stacks_available = None
        self.data_current = None

        # compute the current stack
        self.stack_current = None
        self.len_current_stack_previous_check = 0
        self.len_current_stack = 0
        try:
            self.len_expected = int(self.params['On-the-fly']['max_image'])
        except ValueError as err:
            raise ValueError(f'On-the-fly: {err}')

    def run(self):
        """
        On-the-fly: run preprocessing while data is being written...

        How does it works:
            (loop every n seconds).
            1) Catch mrc|tif files in path (raw or motioncor).
            2) Group the files in tilt-series.
            3) Split stack in two: old stack and current stack. If only one stack, old stack is not defined.
                - old stack: added to the queue if not already processed.
            4) Decide if current stack is finished or not. If so, add to the queue if not already processed.
            5) Send the queue to pre-processing and clear the queue.

        Current stack:
            - The program use a buffer to "remember" how long it's been since the last change in the raw files.
            - When a tilt-series is being written, the buffer will be reset every time a new image (from the
              same stack) is detected. Therefore, the program will tolerate having nothing to send to
              processing for a long time (a tilt-series can be acquired in more than 40min).
            - The user has to specify the expected number of images per stack. The program will send the stack
              to processing if this number is reached.
              NB:   When a tilt-series is send to processing, the program tag this stack as processed and
                    will no longer touch it.
                    If a stack has more images than expected, it becomes ambiguous so the program will stop
                    by raising an AssertationError.

            - Stack with less images than expected:
                - If new images of this stack are detected (the microscope is doing the acquisition of this stack),
                  then the program will wait for it to finish.
                - The tolerated time between images is set by the user. If nothing is written after this
                  tolerated time of inactivity, the tilt-series is send to processing (no matter the number
                  of images) and the program stops. It is the only way I found to process the last tilt-series
                  of an acquisition with missing images...

        NB: If an old stack has less images than expected, the program should handle this without any difficulty.
        NB: Stack that are already processed (toolbox_stack_processed.txt) are already in self.processed (__init__),
            so this function will not send them to pre-processing.
        NB: --stack is ignored: positive selection cannot be used with --fly
        """
        running = True
        while running:
            print(f"\rFly: Buffer = "
                  f"{round(self.buffer * self.time_between_checks)} /{self.buffer_tolerance_sec}sec",
                  end='')

            time.sleep(self.time_between_checks)
            self._get_files()

            # the goal is to identify the tilt-series that are finished and register them in this list
            self.queue = []

            # split the files into the current stack and old stacks if any
            len_avail = len(self.data_stacks_available)
            if len_avail == 1:
                self.stack_current = self.data_stacks_available[0]
            elif len_avail > 1:
                self._get_old_stacks()
            else:
                self.buffer += 1
                if self.buffer == self.buffer_tolerance:
                    running = False
                continue

            # it is more tricky to know what to do with the last stack
            self._analyse_last_stack()

            # if the buffer reaches the limit, it means nothing is happening for too long, so stop
            if self.buffer == self.buffer_tolerance:
                if self.stack_current not in self.processed:
                    self.queue.append(self.stack_current)
                    self.processed.append(self.stack_current)
                running = False

            # send to preprocessing
            if self.queue:
                print('\n')
                self.params['Run']['process_stacks_list'] = self.queue
                preprocessing(self.pObj)

            # reset the length if necessary
            self.len_current_stack_previous_check = self.len_current_stack

    def _exclude_queue(self):
        """
        Extract the stacks already processed from inputs.ba_hidden_queue_filename.
        """
        try:
            with open(self.queue_filename, 'r') as f:
                remove_stack = f.readlines()

                list2remove = []
                for line in remove_stack:
                    line = [int(i) for i in line.strip('\n').strip(' ').strip(':').split(':') if i != '']
                    list2remove += line
                return list2remove

        except IOError:
            # first time running
            return []

    @staticmethod
    def _set_ordered(to_clean):
        """
        Remove redundant values while preserving the order.

        ARGS:
        to_clean (list): a list of values to be cleaned

        RETURNS:
        list
        """
        cleaned = []
        for item in to_clean:
            if item not in cleaned:
                cleaned.append(item)

        return cleaned

    def _get_files_number(self, filename_in):
        filename_split = filename_in.split('/')[-1].split('_')
        return int(''.join(i for i in filename_split[self.field_nb] if i.isdigit()))

    def _get_files(self):
        """
        Catch the raw files in path, order them by time of writing and set the
        number of the stack.
        """
        files = sorted(glob(f'{self.path}/{self.prefix}*.{self.extension}'), key=os.path.getmtime)
        self.data = pd.DataFrame(dict(raw=files))
        self.data['nb'] = self.data['raw'].map(self._get_files_number)
        self.data_stacks_available = self._set_ordered(self.data['nb'])

    def _get_old_stacks(self):
        """
        At this point, we know there is more than one stack.
        Therefore, old stack are finished and can be processed.
        """
        stack_current = self.data_stacks_available[-1]
        if stack_current != self.stack_current:
            self.len_current_stack_previous_check = 0
        self.stack_current = stack_current

        for old_stack in self.data_stacks_available[:-1]:
            if old_stack not in self.processed:
                self.queue.append(old_stack)
                self.processed.append(old_stack)

    def _analyse_last_stack(self):
        self.data_current = self.data[self.data['nb'] == self.stack_current]
        self.len_current_stack = len(self.data_current)
        if self.len_current_stack == self.len_expected:
            if self.stack_current not in self.processed:
                # Stack has not been processed yet and has the expected size: go to pp.
                self.queue.append(self.stack_current)
                self.processed.append(self.stack_current)
                self.len_current_stack = 0
            else:
                # Stack has been processed and has the expected length. It is either:
                # - the last stack of the acquisition.
                # - it is not the last one, we are just waiting for the first image of the next stack.
                # In both cases, we fill the buffer and wait.
                self.buffer += 1

        elif self.len_current_stack < self.len_expected:
            # In most cases, the stack is not finished, but it can be the actual last stack which for some
            # reason has missing images. To differentiate between the two, check the number of images
            # that were there before:
            # - if no new images, increase the self.buffer.
            # - if new images, the stack is just not finished so reset the self.buffer.
            if self.len_current_stack == self.len_current_stack_previous_check:
                self.buffer += 1
            elif self.len_current_stack > self.len_current_stack_previous_check:
                self.buffer = 0
            else:
                raise AssertionError(f'On-the-file: the tilt-series {self.stack_current} has '
                                     f'less images than the previous check.'
                                     f'It is ambiguous, so stop here.')
        else:
            raise AssertionError(f'On-the-file: the tilt-series {self.stack_current} has more images than expected.'
                                 f'It is ambiguous, so stop here.')
