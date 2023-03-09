from sensor.logger import logging
from sensor.exception import SensorException
from sensor.utils import get_collection_as_dataframe
import sys, os


def test_logger_exception():
    logging.info("Starting the test-logger function.")
    try:
        result = 3 / 0
        print(result)
    except Exception as e:
        logging.info("Exception occurred in test_logger()")
        raise SensorException(e, sys)

    logging.info("Test-logger function ended.")


if __name__ == "__main__":
    try:
        get_collection_as_dataframe("APS", "Sensor")
    except Exception as e:
        print(e)
