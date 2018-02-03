import Parser
from core import utils

DICOM_KEY = 'dicom'
CONTOUR_KEY = 'contour'


class DataPoint(object):
    """
    Represents a single data point i.e. mapping of a single dicom and contour file
    """

    __contour_list = None
    __dicom_image = None
    __dicom_path = None
    __contour_path = None
    __is_data_loaded = False

    def __init__(self,  dicom_path, contour_path):
        self.__dicom_path = dicom_path
        self.__contour_path = contour_path

    def load(self):
        """
        Loads the data contained by dicom and contour file
        :return:
        """
        self.__dicom_image = Parser.DicomParser().parse(self.__dicom_path)
        self.__contour_list = Parser.ContourParser().parse(self.__contour_path)
        self.__is_data_loaded = True

    def get_image_and_mask(self):
        """
        Gets image and mask of this data point
        :return: tuple (image, mask)
        """
        if not self.__is_data_loaded:
            self.load()

        height = len(self.__dicom_image['pixel_data'])
        width = len(self.__dicom_image['pixel_data'][0])
        contour_mask = utils.poly_to_mask(self.__contour_list, width, height)
        return (self.__dicom_image['pixel_data'], contour_mask)

    def to_dictionary(self):
        """
        Converts Data Point object to a dictionary with dicom and contour files
        as keys and actual paths as values
        :return: a dictionary {DICOM_KEY: path, CONTOUR_KEY: path}}
        """
        return {DICOM_KEY: self.__dicom_path, CONTOUR_KEY: self.__contour_path}

    @staticmethod
    def load_from_dictionary(dictionary):
        """
        Creates a new Data Point using passed dictionary.
        :param dictionary: {DICOM_KEY: path, CONTOUR_KEY: path}}
        :return: a new DataPoint object
        """
        return DataPoint(dictionary[DICOM_KEY], dictionary[CONTOUR_KEY])
