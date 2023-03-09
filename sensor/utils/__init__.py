import sys

import pandas as pd

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
        raise SensorException(e, sys)
