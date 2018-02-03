"""
This module contains various utility functions related to
file searching and data loading.
"""
import os
import pandas as pd
import logging
import logging.config

from core.DataPoint import DataPoint

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_image_and_masks(data_points):
    """
    Processes each passed data point and collects image
    and mask data
    :param data_points: list of data points to process
    :return: list of tuples (image_data, mask)
    """
    result = []
    for data_point in data_points:
        result.append(data_point.get_image_and_mask())

    return result


def create_data_points(dicom_dir, contour_dir, link_file):
    """
    Creates data point objects from given paths. It matches the dicom and
    contour directory using the link file, only keeps records where corresponding
    dicom and contour files exist and returns the list of data points.

    Note that these DataPoint objects only contain the reference to dicom and
    contour files, actually data is only loaded when get_mask or load
    methods of DataPoints are called.

    :param dicom_dir: path to dicom directory
    :param contour_dir: path to contour file directory
    :param link_file: path to link csv file
    :return: list of DataPoints
    """
    if not os.path.isdir(dicom_dir):
        logger.error('Dicom directory not found at: ' + dicom_dir)
        return

    if not os.path.isdir(contour_dir):
        logger.error('Contour directory not found at: ' + contour_dir)
        return

    if not os.path.isfile(link_file):
        logger.error('Link file not found at: ' + link_file)
        return

    result = []

    link_data = pd.read_csv(link_file)
    for index, row in link_data.iterrows():

        current_dicom_dir = os.path.join(dicom_dir, row['patient_id'])
        if not os.path.isdir(current_dicom_dir):
            logger.info('Skipping the data point, No dicom dir found at:' + current_dicom_dir)

        current_contour_dir = os.path.join(os.path.join(contour_dir, row['original_id']), 'i-contours')
        # print single_contour_dir
        if not os.path.isdir(current_contour_dir):
            logger.info('Skipping the data point, No contour dir found at: ' + current_contour_dir)

        for file_name in os.listdir(current_dicom_dir):
            if not file_name.endswith('.dcm'):
                continue

            dcm_file_number = file_name.replace('.dcm', '')
            contour_file_name = 'IM-0001-' + dcm_file_number.zfill(4) + '-icontour-manual.txt'

            full_dicom_file_path = os.path.join(current_dicom_dir, file_name)
            full_contour_file_path = os.path.join(current_contour_dir, contour_file_name)

            if not os.path.isfile(full_contour_file_path):
                logger.info('no contour file found against: ' + full_dicom_file_path)
                continue

            result.append(DataPoint(full_dicom_file_path, full_contour_file_path))

    return result


def load_all_data(dicom_dir, contour_dir, link_file):
    """
    Loads all data, first it creates list of data points and then populates
    each data point with data by loading the contour and dicom files.
    :param dicom_dir: path to dicom dir
    :param contour_dir: path to contour directory
    :param link_file: path to link csv file
    :return: list of tuples(image_data, mask)
    """
    data_points = create_data_points(dicom_dir, contour_dir, link_file)
    return get_image_and_masks(data_points)
