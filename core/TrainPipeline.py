import random
import json

from core import data_pipeline
from services import kafka_producer

BATCH_SIZE = 8
TOPIC = b'LOAD_DATA_REQUEST_FOR_ML'


class TrainPipeline(object):
    """
    This class represents a machine learning pipeline which requests
    data asynchronously in batches through a Kafa queue.
    """
    __dataset = None

    def load_data(self, dicom_dir, contour_dir, link_file):
        """
        Loads the present in passed directories
        :param dicom_dir: dicom dir path
        :param contour_dir: contour dir path
        :param link_file: link csv file path
        :return:
        """
        self.__dataset = data_pipeline.create_data_points(dicom_dir, contour_dir, link_file)
        if self.__dataset is None:
            raise ValueError('Could not initialize dataset, ensure paths are correct')

    def __get_batch_data(self):
        batch = []
        for index in range(0, BATCH_SIZE):
            random_point = self.__dataset[random.randint(0, len(self.__dataset) - 1)]
            batch.append(random_point.to_dictionary())

        return batch

    def send_batch_load_request(self):
        """
        Builds a random batch from available data and sends a requests
        to worker nodes to actually load the data
        :return:
        """
        batch = json.dumps(self.__get_batch_data())
        # print json.dumps(batch)
        kafka_producer.push(json.dumps(batch), TOPIC)
