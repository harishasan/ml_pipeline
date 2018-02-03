import sys, os

FILEDIR = os.path.dirname(os.path.realpath(__file__))
SOURCEDIR = FILEDIR + '/../../'
sys.path.append(SOURCEDIR)

from core import data_pipeline
from core import Parser, utils

def test_data_loader():
    """
    This test ensures that the data loaded via data pipeline
    is correct by comparing it with manually loading the known
    correct data
    :return:
    """
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    dicom_path = current_dir_path + '/data/dicom'
    contour_path = current_dir_path + '/data/contours'
    link_path = current_dir_path + '/data/link.csv'

    # laod the data using data pipeline module
    result = data_pipeline.load_all_data(dicom_path, contour_path, link_path)
    # 1 valid mapping exist in the data
    assert len(result) == 1
    # result should be a tuple
    # each element of list should be a tuple with size 2
    assert len(result[0]) == 2

    # now load the contour and dicom data manually
    contour_parser = Parser.ContourParser()
    dicom_parser = Parser.DicomParser()

    contour_file = contour_parser.parse(contour_path + '/SC-HF-I-1/i-contours/IM-0001-0048-icontour-manual.txt')
    dicom_image = dicom_parser.parse(dicom_path + '/SCD0000101/1.dcm')['pixel_data']

    # built a mask directly using utility
    masked_contour = utils.poly_to_mask(contour_file, len(dicom_image[0]), len(dicom_image))
    test_mask_result = result[0][1]

    # compare each value in mask returned by pipeline and mask manually created.
    for outer in range(0, len(test_mask_result)):
        for inner in range(0, len(test_mask_result[outer])):
            assert test_mask_result[outer][inner] == masked_contour[outer][inner]
