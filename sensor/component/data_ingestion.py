import os, sys

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from sensor import utils
from sensor.entity import config_entity
from sensor.entity import artifact_entity
from sensor.exception import SensorException
from sensor.logger import logging


class DataIngestion:
    def __init__(self, data_ingestion_config: config_entity.DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise SensorException(e, sys)

    def initiate_data_ingestion(self) -> artifact_entity.DataIngestionArtifact:
        try:
            logging.info("Exporting Collection data as  Dataframe.")
            df: pd.DataFrame = utils.get_collection_as_dataframe(self.data_ingestion_config.database_name,
                                                                 self.data_ingestion_config.collection_name)
            # Save data in feature store
            df.replace(to_replace="na", value=np.nan, inplace=True)

            # Create Feature Store Folder
            feature_store_dir = os.path.dirname(self.data_ingestion_config.feature_store_file_path)
            os.makedirs(feature_store_dir, exist_ok=True)

            logging.info("Save data in feature store")
            # Save df to feature store folder
            df.to_csv(path_or_buf=self.data_ingestion_config.feature_store_file_path, index=False, header=True)

            # Split dataset into train & test data
            train_df, test_df = train_test_split(df, test_size=self.data_ingestion_config.test_size)

            # Create Train Folder
            train_dir = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(train_dir, exist_ok=True)

            logging.info("Save data in train folder")
            # Save df to train folder
            train_df.to_csv(path_or_buf=self.data_ingestion_config.train_file_path, index=False, header=True)

            # Create Test Folder
            test_dir = os.path.dirname(self.data_ingestion_config.test_file_path)
            os.makedirs(test_dir, exist_ok=True)

            logging.info("Save data in test folder")
            # Save df to test folder
            test_df.to_csv(path_or_buf=self.data_ingestion_config.test_file_path, index=False, header=True)

            # Prepare Data_Ingestion Artifact

            data_ingestion_artifact = artifact_entity.DataIngestionArtifact(
                self.data_ingestion_config.feature_store_file_path,
                self.data_ingestion_config.train_file_path,
                self.data_ingestion_config.test_file_path)

            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise SensorException(e, sys)
