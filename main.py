from sensor.logger import logging
from sensor.exception import SensorException
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
        test_logger_exception()
    except Exception as e:
        print(e)
