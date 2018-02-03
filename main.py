"""
A utility file to run the data pipeline or ml (batch) pipeline
"""
import os
import time
import logging
import logging.config

from core import data_pipeline
from core.TrainPipeline import TrainPipeline

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DICOM_PATH = CURRENT_DIR + '/data/final_data/dicoms'
CONTOUR_PATH = CURRENT_DIR + '/data/final_data/contourfiles'
LINK_PATH = CURRENT_DIR + '/data/final_data/link.csv'


def run_normal_pipeline():
    """
    runs normal pipeline which creates and loads all data points
    :return:
    """
    logger.info('running normal data pipeline')
    results = data_pipeline.load_all_data(DICOM_PATH, CONTOUR_PATH, LINK_PATH)
    logger.info('total records found: ' + str(len(results)))


def run_train_pipeline():
    """
    Starts a ML pipeline which sends data send async batch load requests.
    It runs indefinitely.
    :return:
    """
    logger.info('running ml batch pipeline')
    ml_pipeline = TrainPipeline()
    ml_pipeline.load_data(DICOM_PATH, CONTOUR_PATH, LINK_PATH)

    while True:
        logger.info('requesting new batch of 8')
        ml_pipeline.send_batch_load_request()
        time.sleep(3)


if __name__== "__main__":
    # run_normal_pipeline()
    run_train_pipeline()
