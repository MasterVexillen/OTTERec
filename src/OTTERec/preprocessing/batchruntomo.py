"""
OTTERec.preprocessing.batchruntomo

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 08-Mar-2021

Disclaimer: Adopted and modified from toolbox_tomoDLS.py script at Diamond
"""

import subprocess
import multiprocess as mp


ADOC = f"""
setupset.currentStackExt = st
setupset.copyarg.stackext = st
setupset.copyarg.montage = 0
setupset.copyarg.skip = 
setupset.copyarg.bskip = 
runtime.PatchTracking.any.rawBoundaryModel = 
setupset.systemTemplate = /opt/modules/imod/4.11.1/IMOD/SystemTemplate/cryoSample.adoc
runtime.Preprocessing.any.removeXrays = 1
comparam.prenewst.newstack.BinByFactor = 8
runtime.Fiducials.any.trackingMethod = 1
setupset.copyarg.gold = 0
comparam.xcorr_pt.tiltxcorr.SizeOfPatchesXandY = 300,200
comparam.xcorr_pt.imodchopconts.LengthOfPieces = -1
runtime.AlignedStack.any.binByFactor = 8
comparam.tilt.tilt.THICKNESS = 3600
runtime.Trimvol.any.scaleFromZ = 
runtime.Postprocess.any.doTrimvol = 1
runtime.Positioning.any.thickness = 3600
setupset.copyarg.pixel = 0.163
setupset.copyarg.rotation = 86
setupset.copyarg.userawtlt = 1
runtime.Excludeviews.any.deleteOldFiles = 0
comparam.xcorr_pt.tiltxcorr.NumberOfPatchesXandY = 12,8
comparam.xcorr_pt.tiltxcorr.ShiftLimitsXandY = 2,2
comparam.xcorr_pt.tiltxcorr.IterateCorrelations = 4
runtime.PatchTracking.any.adjustTiltAngles = 1
comparam.align.tiltalign.MagOption = 0
comparam.align.tiltalign.TiltOption = 0
comparam.align.tiltalign.RotOption = 3
comparam.align.tiltalign.BeamTiltOption = 0
runtime.Trimvol.any.reorient = 2
"""

class Batchruntomo:
    """
    Class encapsulating a Batchruntomo object
    """

    def __init__(self, paramsObj, stack_filename, stack_path):
        """
        Initialise a Batchruntomo object

        ARGS:
        paramsObj (Params): Parmas object including all input parameters
        stack_filename (str): default filename for the stacks
        stack_path (str): default path for the stacks
        """

        self.pObj = paramsObj
        self.params = self.pObj.params

        self.rootname = stack_filename.split('/')[-1].replace('.st', '')
        self.path = stack_path[:-1] # have to remove the trailing /
        self.filename_adoc = f'{self.path}/tool_preprocessing.adoc'
        self.first_run = True
        self.log = f'\tBatchruntomo:\n'

        self._create_adoc()

        # first run
        self.first_run = True
        batchruntomo = subprocess.run(self._get_batchruntomo(),
                                      stdout=subprocess.PIPE,
                                      encoding='ascii')
        self.first_run = False
        self.stdout = batchruntomo.stdout

        # There is a small bug in the IMOD install. David said it will be fixed in the next release.
        # Basically, one cannot change the residual report threshold. So run batchruntomo first,
        # up to tiltalign in order to have align.com and then modify align.com and restart from there.

        if 'ABORT SET:' in self.stdout:
            self._get_batchruntomo_log(abort=True)
        elif self.params['BatchRunTomo']['step_end'] > 6:
            # change the threshold in align.com
            with open(f'{self.path}/align.com', 'r') as align:
                f = align.read().replace('ResidualReportCriterion\t3', 'ResidualReportCriterion\t1')
            with open(f'{self.path}/align.com', 'w') as corrected_align:
                corrected_align.write(f)

            # second run with correct report threshold
            batchruntomo = subprocess.run(self._get_batchruntomo(),
                                          stdout=subprocess.PIPE,
                                          encoding='ascii')
            self.stdout += batchruntomo.stdout
            self._get_batchruntomo_log()

    def _create_adoc(self):
        """
        Create an adoc file from default adoc or using specified adoc file directly.
        """
        if self.params['BatchRunTomo']['adoc_file'] == 'default':
            # compute bin coarsed using desired pixel size
            self.params['BatchRunTomo']['coarse_align_bin_size'] = \
                round(float(self.params['BatchRunTomo']['bead_size']) /
                      (12.5 * 0.1 * self.params['MotionCor']['desired_pixel_size']))

            adoc_file = ADOC
            convert_dict = {
                'ba_brt_gold_size': self.params['BatchRunTomo']['bead_size'],
                'ba_brt_rotation_angle': self.params['BatchRunTomo']['init_rotation_angle'],
                'ad_brt_bin_coarse': self.params['BatchRunTomo']['coarse_align_bin_size'],
                'ad_brt_target_nb_beads': self.params['BatchRunTomo']['target_num_beads'],
                'ad_brt_bin_ali': self.params['BatchRunTomo']['final_bin'],
            }
            for param in ('ba_brt_gold_size',
                          'ba_brt_rotation_angle',
                          'ad_brt_bin_coarse',
                          'ad_brt_target_nb_beads',
                          'ad_brt_bin_ali'):
                adoc_file = adoc_file.replace(f'<{param}>', f'{convert_dict[param]}')

            with open(self.filename_adoc, 'w') as file:
                file.write(adoc_file)
        else:
            if os.path.isfile(self.params['BatchRunTomo']['adoc_file']):
                self.filename_adoc = self.params['BatchRunTomo']['adoc_file']
            else:
                self.params['BatchRunTomo']['adoc_file'] = 'default'
                self._create_adoc(self.pObj)

    def _get_batchruntomo(self):
        temp_end = 6 if self.params['BatchRunTomo']['step_end'] >= 6 else self.params['BatchRunTomo']['step_end']
        temp_gpu = self.params['MotionCor']['use_gpu'][0]
        temp_cpu = [str(i) for i in range(1, mp.cpu_count()+1)]
        if self.first_run:
            cmd = ['batchruntomo',
                   '-CPUMachineList', f"{temp_cpu}",
                   '-GPUMachineList', '1',
                   '-DirectiveFile', self.filename_adoc,
                   '-RootName', self.rootname,
                   '-CurrentLocation', self.path,
                   '-StartingStep', str(self.params['BatchRunTomo']['step_start']),
                   '-EndingStep', f"{temp_end}",
            ]
        else:
            cmd = ['batchruntomo',
                   '-CPUMachineList', f"{temp_cpu}",
                   '-GPUMachineList', '1',
                   '-DirectiveFile', self.filename_adoc,
                   '-RootName', self.rootname,
                   '-CurrentLocation', self.path,
                   '-StartingStep', f"{temp_end+1}",
                   '-EndingStep', str(self.params['BatchRunTomo']['step_end']),
            ]
        return cmd

    def _get_batchruntomo_log(self, abort=False):
        self.stdout = self.stdout.split('\n')

        if abort:
            for line in self.stdout:
                if 'ABORT SET:' in line:
                    self.log += f'\t{line}.\n'
            return

        # erase.log
        self.log += self._get_batchruntomo_log_erase(f'{self.path}/eraser.log')

        # stats.log, cliphist.log and track.log
        # easier to catch the info directly in main log
        for line in self.stdout:
            if 'Views with locally extreme values:' in line:
                self.log += f'\t\t- Stats: {line}.\n'
            elif 'low SDs or dark regions' in line:
                self.log += f'\t\t- Cliphist: {line}.\n'
            elif 'total points accepted' in line:
                self.log += f"\t\t- Autofidseed: {line.split('=')[-1]} beads accepted as fiducials.\n"

        # track.log
        self.log += self._get_batchruntomo_log_track(f'{self.path}/track.log')

        # restricalign.log
        for line in self.stdout:
            if 'restrictalign: Changed align.com' in line:
                self.log += f'\t\t- Restrictalign: Restriction were applied to statisfy measured/unknown ratio.\n'
                break
            elif 'restrictalign: No restriction of parameters needed' in line:
                self.log += f'\t\t- Restrictalign: No restriction of parameters needed.\n'
                break

        self.log += self._get_batchruntomo_log_align(self.stdout)

    @staticmethod
    def _get_batchruntomo_log_erase(log):
        # catch number of pixel replaced and if program succeeded
        exit_status = 'Not found'
        try:
            with open(log, 'r') as file:
                count_pixel = 0
                for line in file:
                    if 'replaced in' in line:
                        count_pixel += int(line.split()[3])
                    elif 'SUCCESSFULLY COMPLETED' in line:
                        exit_status = 'Succeded'
            log = f'\t\t- Erase: {count_pixel} pixels were replaced. Exit status: {exit_status}.\n'
        except IOError:
            log = f'\t\terase.log is missing... Alignment may have failed.\n'
        return log

    @staticmethod
    def _get_batchruntomo_log_track(log):
        # track.log
        exit_status = 'Not found'
        try:
            with open(log, 'r') as file:
                missing_points = 0
                for line in file:
                    if 'Total points missing =' in line:
                        missing_points = line.split(' ')[-1].strip('\n')
                    elif 'SUCCESSFULLY COMPLETED' in line:
                        exit_status = 'Succeded'
            log = f'\t\t- Track beads: {missing_points} missing points. Exit status: {exit_status}.\n'
        except IOError:
            log = f'\t\ttrack.log is missing... Alignment may have failed.\n'
        return log

    @staticmethod
    def _get_batchruntomo_log_align(log):
        residual_error_mean_and_sd = 'Residual error mean and sd: None.'
        residual_error_weighted_mean = 'Residual error weighted mean: None'
        residual_error_local_mean = 'Residual error local mean: None'
        weighted_error_local_mean = 'Weighted error local mean: None'
        for line in log:
            if 'Residual error mean and sd:' in line:
                residual_error_mean_and_sd = line.strip()
            if 'Residual error weighted mean:' in line:
                residual_error_weighted_mean = line.strip()
            if 'Residual error local mean:' in line:
                residual_error_local_mean = line.strip()
            if 'Weighted error local mean:' in line:
                weighted_error_local_mean = line.strip()

        return (f'\t\t{residual_error_mean_and_sd}\n'
                f'\t\t{residual_error_weighted_mean}\n'
                f'\t\t{residual_error_local_mean}\n'
                f'\t\t{weighted_error_local_mean}\n')
