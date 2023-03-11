from sensor.logger import logging
from sensor.exception import SensorException
from sensor.utils import get_collection_as_dataframe
import sys, os
from sensor.entity.config_entity import TrainingPipelineConfig
from sensor.entity.config_entity import DataIngestionConfig
from sensor.component import data_ingestion

# def test_logger_exception():
#     logging.info("Starting the test-logger function.")
#     try:
#         result = 3 / 0
#         print(result)
#     except Exception as e:
#         logging.info("Exception occurred in test_logger()")
#         raise SensorException(e, sys)
#
#     logging.info("Test-logger function ended.")


if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        print(data_ingestion_config.to_dict())
        data_ingestion = data_ingestion.DataIngestion(data_ingestion_config = data_ingestion_config)
        print(data_ingestion.initiate_data_ingestion())
    except Exception as e:
        print(e)
