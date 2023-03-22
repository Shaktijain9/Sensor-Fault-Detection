import sys
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from sensor import utils
from sensor.entity import artifact_entity
from sensor.entity import config_entity
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.config import TARGET_COLUMN


class DataValidation:
    def __init__(self, data_validation_config: config_entity.DataValidationConfig,
                 data_ingestion_artifact: artifact_entity.DataIngestionArtifact):
        logging.info("-------Data Validation -------")
        try:
            logging.info(f'Data Validation')
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.validation_error = dict()
        except Exception as e:
            raise SensorException(e, sys)

    def is_required_column_exist(self, base_df: pd.DataFrame, current_df: pd.DataFrame, report_key_name: str) -> bool:
        try:
            logging.info('is_required_column_exist method started.')
            base_columns = base_df.columns
            curr_columns = current_df.columns
            missing_columns = []

            logging.info('Checking whether the column is missing or not.')
            for base_column in base_columns:
                if base_column not in curr_columns:
                    missing_columns.append(base_column)

            logging.info('Generating Missing columns report.')
            if len(missing_columns) > 0:
                self.validation_error[report_key_name] = missing_columns
                return False
            return True
            logging.info('is_required_column_exist method ended.')

        except Exception as e:
            raise SensorException(e, sys)

    def data_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, report_key_name: str):
        try:
            logging.info('data_drift method started.')
            drift_report = dict()
            base_columns = base_df.columns

            # Null Hypothesis : Both the distributions are same.
            # Alternate Hypothesis : Distributions are not same.
            logging.info('Checking data drift for each column available.')
            for base_column in base_columns:
                base_data, curr_data = base_df[base_column], current_df[base_column]
                is_same_distribution = ks_2samp(base_data, curr_data)

                logging.info('Entering data-drift result.')
                if is_same_distribution.pvalue > 0.05:
                    # Accepting Null Hypothesis
                    drift_report[base_column] = {
                        "pvalue": float(is_same_distribution.pvalue),
                        "same_distribution": True
                    }
                else:
                    # Rejecting Null Hypothesis
                    drift_report[base_column] = {
                        "pvalue": float(is_same_distribution.pvalue),
                        "same_distribution": False
                    }

            self.validation_error[report_key_name] = drift_report
            logging.info('data_drift method ended.')


        except Exception as e:
            raise SensorException(e, sys)

    def drop_column(self, df: pd.DataFrame, report_key_name: str) -> Optional[pd.DataFrame]:
        """
        This method drops columns whose missing values are more than threshold.
        :param df: dataframe
        :param report_key_name:
        :param threshold: Criteria for accepted missing values in a column
        :return: dataframe with dropped columns whose missing values were more than threshold.
        """

        try:
            logging.info('drop_column method started.')
            threshold = self.data_validation_config.drop_threshold
            null_report = df.isna().sum() / df.shape[0]
            # Column names with null value greater than threshold.
            drop_column_names = null_report[null_report > threshold].index

            logging.info(f"Columns to drop : {list(drop_column_names)}")
            self.validation_error[report_key_name] = list(drop_column_names)

            df.drop(list(drop_column_names), axis=1, inplace=True)

            # Return None if no columns left
            if len(df.columns) == 0:
                return None
            else:
                return df
            logging.info('drop_column method ended.')


        except Exception as e:
            raise SensorException(e, sys)

    def initiate_validation(self) -> artifact_entity.DataValidationArtifact:
        try:
            logging.info('initiate column method started.')
            base_df = pd.read_csv(self.data_validation_config.base_file_path)
            base_df.replace({'na': np.NAN}, inplace=True)

            # Drop missing values
            base_df = self.drop_column(df=base_df, report_key_name='missing_values_within_base_dataset')

            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            train_df = self.drop_column(df=train_df, report_key_name='missing_values_within_train_dataset')
            test_df = self.drop_column(df=test_df, report_key_name='missing_values_within_test_dataset')

            exclude_columns = [TARGET_COLUMN]
            base_df = utils.convert_columns_float(base_df, exclude_columns=exclude_columns)
            train_df = utils.convert_columns_float(train_df, exclude_columns=exclude_columns)
            test_df = utils.convert_columns_float(test_df, exclude_columns=exclude_columns)

            train_col_status = self.is_required_column_exist(base_df=base_df, current_df=train_df,
                                                             report_key_name='missing_columns_within_train_dataset')
            test_col_status = self.is_required_column_exist(base_df=base_df, current_df=test_df,
                                                            report_key_name='missing_columns_within_test_dataset')

            if train_col_status:
                self.data_drift(base_df=base_df, current_df=train_df, report_key_name='data_drift_within_train_dataset')

            if test_col_status:
                self.data_drift(base_df=base_df, current_df=test_df, report_key_name='data_drift_within_test_dataset')

            # Write the report
            logging.info('Writing report in yaml file.')

            utils.write_yaml_file(file_path=self.data_validation_config.report_file_path,
                                  data=self.validation_error)

            logging.info('initiate column method ended.')
            data_validation_artifact = artifact_entity.DataValidationArtifact(
                report_file_path=self.data_validation_config.report_file_path)
            return data_validation_artifact

        except Exception as e:
            raise Exception(e, sys)
