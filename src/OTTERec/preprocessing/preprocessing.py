"""
OTTERec.preprocessing.preprocessing

Copyright (C) 2021 Rosalind Franklin Institute

Author: Neville B.-y. Yee
Date: 09-Mar-2021

Disclaimer: adopted and modified from toolbox_tomoDLS.py from DLS repo
"""

import os

import OTTERec.preprocessing.metadata as metadata
import OTTERec.preprocessing.worker as worker
import OTTERec.preprocessing.motioncor as mc


def preprocessing(paramsObj, loggerObj):
    """
    Each tilt-series is treated sequentially, but most steps are asynchronous.
    See individual function fore more detail.

    ARGS:
    paramsObj (Params): Params object (from reading YAML) containing input parameters
    loggerObj (Logger): Logger object for logging progress
    """
    params = paramsObj.params

    # set output directories
    os.makedirs(params['Outputs']['MotionCor2_path'], exist_ok=True)
    os.makedirs(params['Outputs']['stacks_path'], exist_ok=True)

    loggerObj('Start preprocessing.')

    mObj = metadata.Metadata(paramsObj)
    meta = mObj.get_metadata()

    # once the metadata is loaded, set its pixel size and calculate Ftbin
    inputs.set_pixelsize(meta)

    # some stdout
    logger(f"Collecting data:\n"
           f"\tRaw images: {mObj.stacks_len}\n"
           f"\tTilt-series: {mObj.stacks_nb}\n"
           f"\tPossible nb of images per stack: {mObj.stacks_images_per_stack}")
    if params['MotionCor']['run_MotionCor2']:
        gpu_list = params['MotionCor']['use_gpu']
        logger(f"Starting MotionCor on GPU {', '.join([str(gpu) for gpu in gpu_list])}:")

    wObj = worker.WorkerManager(mObj.stacks_nb, paramsObj)

    # compute sequentially each tilt-series
    # first run MotionCor, then stack and ctffind, both in parallel
    for tilt_number in mObj.stacks_nb:
        meta_tilt = meta[meta['nb'] == tilt_number]

        if params['MotionCor']['run_MotionCor2']:
            mc.MotionCor(paramsObj, meta_tilt, tilt_number)

        # communicate the job to workers
        job2do = [tilt_number, meta_tilt, paramsObj]
        if params['CTFFind']['run_ctffind']:
            wObj.new_async(Ctffind, job2do)
        if params['Run']['create_stack'] or \
           params['BatchRunTomo']['align_image_brt']:
            wObj.new_async(Stack, job2do)

    # wrap everything up
    wObj.close()
    mObj.save_processed_stack()
