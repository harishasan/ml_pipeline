"""
This service is responsible for sending messages to a kafka topic
"""
import os
from kafka import KafkaProducer


KAFKA_ADDRESS_VAR_NAME = 'KAFKA_ADDRESS'
KAFKA_ADDRESS = os.environ[KAFKA_ADDRESS_VAR_NAME ] if KAFKA_ADDRESS_VAR_NAME in os.environ else 'localhost:9092'
PRODUCER = KafkaProducer(bootstrap_servers=KAFKA_ADDRESS)


def push(serialized_data, topic):
    """
    puts message on a kafka topic
    :param serialized_data: data to send
    :param topic: topic to send data onto
    :return:
    """
    PRODUCER.send(topic, serialized_data)
