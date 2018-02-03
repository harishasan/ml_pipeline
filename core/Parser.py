import dicom
from dicom.errors import InvalidDicomError


class Parser(object):
    """
    abstract base class for various parsers
    """
    def parse(self, file_path):
        pass


class DicomParser(Parser):
    """
    Dicom parser
    """
    def parse(self, file_path):
        """Parse the given DICOM filename

        :param filename: filepath to the DICOM file to parse
        :return: dictionary with DICOM image data
        """

        try:
            dcm = dicom.read_file(file_path)
            dcm_image = dcm.pixel_array

            try:
                intercept = dcm.RescaleIntercept
            except AttributeError:
                intercept = 0.0
            try:
                slope = dcm.RescaleSlope
            except AttributeError:
                slope = 0.0

            if intercept != 0.0 and slope != 0.0:
                dcm_image = dcm_image * slope + intercept
            dcm_dict = {'pixel_data': dcm_image}
            return dcm_dict
        except InvalidDicomError:
            return None


class ContourParser(Parser):
    """
    Contour parser
    """
    def parse(self, file_path):
        """Parse the given contour filename

            :param filename: filepath to the contourfile to parse
            :return: list of tuples holding x, y coordinates of the contour
            """

        coords_lst = []

        with open(file_path, 'r') as infile:
            for line in infile:
                coords = line.strip().split()

                x_coord = float(coords[0])
                y_coord = float(coords[1])
                coords_lst.append((x_coord, y_coord))

        return coords_lst




