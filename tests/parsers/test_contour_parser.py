import sys, os

FILEDIR = os.path.dirname(os.path.realpath(__file__))
SOURCEDIR = FILEDIR + '/../../'
sys.path.append(SOURCEDIR)

from core import Parser

def test_data_loader():
    """
    This test ensures that the data loaded by contour parseris correct
    by comparing it with known data
    :return:
    """
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    contour_path = current_dir_path + '/data/contour_test.txt'

    contour = Parser.ContourParser()
    contour_data = contour.parse(contour_path)

    assert len(contour_data) == 10
    assert contour_data[0][0] == 120.50
    assert contour_data[0][1] == 137.50
    assert contour_data[9][0] == 123.00
    assert contour_data[9][1] == 133.00
