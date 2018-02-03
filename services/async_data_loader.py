import os
import json
import sys
import pickle
import logging
import logging.config

from kafka import KafkaConsumer

FILEDIR = os.path.dirname(os.path.realpath(__file__))
SOURCEDIR = FILEDIR + '/../'
sys.path.append(SOURCEDIR)

from core.DataPoint import DataPoint
from services import kafka_producer

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

KAFKA_ADDRESS_VAR_NAME = 'KAFKA_ADDRESS'
KAFKA_ADDRESS = os.environ[KAFKA_ADDRESS_VAR_NAME] if KAFKA_ADDRESS_VAR_NAME in os.environ else 'localhost:9092'
SOURCE_TOPIC = b'LOAD_DATA_REQUEST_FOR_ML'
TARGET_TOPIC = b'LOAD_DATA_RESPONSE_FOR_ML'


class KafkaDataProcessor(object):
    """
    This class creates a worker which listens to a kafka topic.
    Worked pulls the messages does the data processing on batch
    sent by produces and puts the result into another kafka topic
    """
    kafka_consumer = None

    def __init__(self):
        self.kafka_consumer = KafkaConsumer(SOURCE_TOPIC, bootstrap_servers=KAFKA_ADDRESS)

    def start(self):
        """
        Starts listening for new messages
        :return:
        """
        logger.info('wating for message in queue')
        for msg in self.kafka_consumer:

            images_array = []
            target_array = []

            dictionary_list = json.loads(json.loads(msg.value))

            for item in dictionary_list:
                data_point = DataPoint.load_from_dictionary(item)
                result = data_point.get_image_and_mask()
                images_array.append(result[0])
                target_array.append(result[1])

            result = (images_array, target_array)
            serialized = pickle.dumps(result)
            kafka_producer.push(serialized, TARGET_TOPIC)
            logger.info('message processed successfully')


if __name__ == "__main__":
    consumer = KafkaDataProcessor()
    consumer.start()
