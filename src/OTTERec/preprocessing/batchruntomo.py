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
# INPUT FILE BATCHRUNTOMO #

# Setup #
setupset.copyarg.gold = <ba_brt_gold_size>
setupset.copyarg.rotation = <ba_brt_rotation_angle>
setupset.copyarg.voltage = 300
setupset.copyarg.Cs = 2.7
setupset.copyarg.dual = 0
setupset.copyarg.userawtlt = 1
setupset.scanHeader = 1


# Preprocessing #
runtime.Preprocessing.any.removeXrays = 1
runtime.Preprocessing.any.archiveOriginal = 0
runtime.Preprocessing.any.endExcludeCriterion = 0
runtime.Preprocessing.any.darkExcludeRatio = 0.17
runtime.Preprocessing.any.darkExcludeFraction = 0.33
runtime.Preprocessing.any.removeExcludedViews = 0

#comparam.eraser.ccderaser.BoundaryObjects = 3
comparam.eraser.ccderaser.PeakCriterion = 10.
comparam.eraser.ccderaser.DiffCriterion = 8.
comparam.eraser.ccderaser.MaximumRadius = 4.2

# Coarse alignment #
comparam.xcorr.tiltxcorr.ExcludeCentralPeak = 1
comparam.xcorr.tiltxcorr.FilterRadius2 = 0.25
comparam.xcorr.tiltxcorr.FilterSigma2 = 0.05
comparam.prenewst.newstack.BinByFactor = 6
comparam.prenewst.newstack.AntialiasFilter = -1
comparam.prenewst.newstack.ModeToOutput =


# Seeding and tracking #
runtime.Fiducials.any.trackingMethod = 1
runtime.Fiducials.any.seedingMethod = 0

comparam.xcorr_pt.tiltxcorr.SizeOfPatchesXandY = 300, 300
comparam.xcorr_pt.tiltxcorr.OverlapOfPatchesXandY = 0.33, 0.33
comparam.xcorr_pt.tiltxcorr.IterateCorrelations = 4
comparam.xcorr_pt.tiltxcorr.FilterSigma1 = 0.03
comparam.xcorr_pt.tiltxcorr.FilterRadius2 = 0.25
comparam.xcorr_pt.tiltxcorr.FilterSigma2 = 0.05
#comparam.xcorr_pt.tiltxcorr.BordersinXandY = 48, 34

comparam.track.beadtrack.LocalAreaTracking = 1
comparam.track.beadtrack.SobelFilterCentering = 1
comparam.track.beadtrack.KernelSigmaForSobel = 1.5
comparam.track.beadtrack.RoundsOfTracking = 4

# comparam.autofidseed.autofidseed.TargetNumberOfBeads = <ad_brt_target_nb_beads>
# comparam.autofidseed.autofidseed.AdjustSizes = 1
# comparam.autofidseed.autofidseed.TwoSurfaces = 1
# comparam.autofidseed.autofidseed.MinGuessNumBeads = 20


# Tomogram positioning #
runtime.Positioning.any.sampleType = 2
runtime.Positioning.any.wholeTomogram = 1
runtime.Positioning.any.binByFactor = 6
runtime.Positioning.any.thickness = 3000

runtime.Positioning.any.hasGoldBeads = 0
comparam.cryoposition.cryoposition.BinningToApply = 6


# Alignment #
comparam.align.tiltalign.SurfacesToAnalyze = 1
comparam.align.tiltalign.LocalAlignments = 0
comparam.align.tiltalign.RobustFitting = 0
comparam.align.tiltalign.WeightWholeTracks = 1
comparam.align.tiltalign.ResidualReportCriterion = 3.0

#comparam.align.tiltalign.MagOption = 0
#comparam.align.tiltalign.TiltOption = 0
#comparam.align.tiltalign.RotOption = -1
#comparam.align.tiltalign.BeamTiltOption = 2

runtime.TiltAlignment.any.enableStretching = 0
runtime.PatchTracking.any.adjustTiltAngles = 0
runtime.RestrictAlign.any.targetMeasurementRatio = 4


# Final aligned stack #
runtime.AlignedStack.any.correctCTF = 0
runtime.AlignedStack.any.eraseGold = 0
runtime.AlignedStack.any.filterStack = 0
runtime.AlignedStack.any.binByFactor = <ad_brt_bin_ali>
runtime.AlignedStack.any.linearInterpolation = 1
comparam.newst.newstack.AntialiasFilter = 1

runtime.GoldErasing.any.extraDiameter = 4
runtime.GoldErasing.any.thickness = 1000
comparam.golderaser.ccderaser.ExpandCircleIterations = 3


# Reconstruction #
comparam.tilt.tilt.THICKNESS = 5000
comparam.tilt.tilt.FakeSIRTiterations = 8
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
