import os
import sys

import pandas as pd
import yaml

from sensor.config import mongo_client
from sensor.exception import SensorException
from sensor.logger import logging


def get_collection_as_dataframe(database_name: str, collection_name: str) -> pd.DataFrame:
    """
    This function returns mongo collection as dataframe
    :param database_name:
    :param collection_name:
    :return: pandas dataframe
    """
    try:
        logging.info(f"Reading data from {database_name} & {collection_name}")
        df = pd.DataFrame(list(mongo_client[database_name][collection_name].find({}, {'_id': 0})))
        logging.info(f"Columns found : {df.columns}")
        logging.info(f"Dataframe with shape : {df.shape} is obtained.")
        return df
    except Exception as e:
        raise e


def write_yaml_file(file_path: str, data: dict):
    """
    :param file_path: yaml filepath
    :param data: data to written in the yaml file
    :return: None
    """
    try:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        with open(file_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file)

    except Exception as e:
        raise SensorException(e, sys)

def convert_columns_float(df:pd.DataFrame, exclude_columns:list):
    try:
        for column in df.columns:
            if column not in exclude_columns:
                df[column] = df[column].astype('float')
        return df
    except Exception as e:
        raise e

